import socket
import json

import shieldnoc.protocol as protocol

from threading import Thread
from select import select
from shieldnoc.logging_config import logger
from shieldnoc.server.core.connection.chat_manager import ChatManager
from shieldnoc.server.core.connection.vpn_manager import VPNManager


class ConnectionManager:
    CHAT_PREFIX = "0"
    VPN_PREFIX = "3"

    def __init__(self):
        self.chat_manager = ChatManager(self.broadcast_msg)
        self._vpn_manager = VPNManager()
        self._stop_connection_event = self.chat_manager.stop_connection_event

        self._listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listen_sock.settimeout(1.0)

        try:
            self._listen_sock.bind((protocol.LISTEN_EVERYONE_IP, protocol.LISTEN_PORT))

        except Exception as e:
            logger.error("Server encountered with a problem while trying to establish connection")
            logger.error("Failed to bind socket: " + str(e))
            exit()

        self._listen_sock.listen()
        logger.info("===== ShieldNOC connection is up and running =====")

        self._clients: dict[socket.socket, tuple[str, int]] = {}  # [socket: (ip, port)]

    def start_connection(self):
        thread = Thread(target=self._clients_acceptor)
        thread.start()
        logger.info("===== ShieldNOC is ready for accepting clients =====")

    def _clients_acceptor(self) -> None:
        while not self._stop_connection_event.is_set():
            try:
                client_sock, client_addr = self._listen_sock.accept()
            except socket.timeout:
                continue

            if self._vpn_manager.is_ip_in_current_use(client_addr(0)):
                thread = Thread(target=self._handle_client, args=(client_sock,))
                client_sock.settimeout(1.0)
                self._clients[client_sock] = client_addr
            else:
                thread = Thread(target=self._initial_connection, args=(client_sock,))
                client_sock.settimeout(5.0)
            thread.start()

        logger.info(">>> ShieldNOC System Closed <<<")

    def _initial_connection(self, client_sock: socket.socket) -> None:
        client_addr = client_sock.getpeername()
        logger.info(f"{client_addr} starts the connection process to ShieldNOC System")

        try:
            valid_msg, client_msg = protocol.get_payload(client_sock)

            if valid_msg:
                prefix = client_msg[0]

                if prefix != self.VPN_PREFIX:
                    protocol.send_segment(client_sock, "Initial connection must start with VPN request")
                    return

                content = client_msg[1:]  # client public key
                server_public_key, client_assigned_vpn_ip = self._vpn_manager.add_peer(content)
                vpn_conf_data = {
                    "server_public_key": server_public_key,
                    "assigned_vpn_ip": client_assigned_vpn_ip
                }
                data = self._encrypt_data(json.dumps(vpn_conf_data))  # TODO: add encryption
                protocol.send_segment(client_sock, self.VPN_PREFIX + data)

            else:
                logger.error(f"Error with sending the content: {client_msg}")
                if client_msg in (ConnectionResetError.__name__, ConnectionAbortedError.__name__):
                    return

        except Exception as e:
            logger.error(f"Initial connection failed: {e}")

        finally:
            client_sock.close()

    def _handle_client(self, client_sock: socket.socket) -> None:
        client_addr = client_sock.getpeername()

        logger.info(f"{client_addr} has connected to ShieldNOC System")
        self.chat_manager.handle_system_msg(f"~{client_addr[0]} joined the ShieldNOC System~")

        while not self._stop_connection_event.is_set():
            try:
                valid_msg, client_msg = protocol.get_payload(client_sock)
            except socket.timeout:
                continue

            except Exception as e:
                logger.warning(f"Unexpected Error occurred: {e}")
                break

            if valid_msg:
                prefix = client_msg[0]
                content = client_msg[1:]

                if prefix == self.CHAT_PREFIX:
                    self.chat_manager.handle_client_msg(client_addr[0], content)
                elif prefix == self.VPN_PREFIX:
                    pass  # TODO: add api_to_vpn_somehow
                else:
                    logger.warning("Got a valid client msg with invalid prefix")

            else:
                logger.error(f"Error with sending the content: {client_msg}")

                if client_msg in (ConnectionResetError.__name__, ConnectionAbortedError.__name__):
                    break

                try:
                    while True:
                        readable, _, _ = select([client_sock], [], [], 0)
                        if not readable:
                            break
                        client_sock.recv(1024)  # Attempt to empty the socket from possible garbage

                except ConnectionResetError:
                    logger.warning("Client unexpectedly closed the connection in a middle of reading data")
                    break

                except Exception as e:
                    logger.warning(f"Unexpected Error occurred while trying of empty the socket: {e} ")

        # broken | Event raised
        self._clients.pop(client_sock)
        # TODO: update what needs in DB
        client_sock.close()
        logger.info(f"> ShieldNOC System End Session With Client {client_addr} <")

    def end_chat_session(self):
        self._stop_connection_event.set()

    def broadcast_msg(self, msg) -> None:
        for client_sock in self._clients:
            protocol.send_segment(client_sock, self.CHAT_PREFIX + msg)

    @staticmethod
    def _encrypt_data(data: str) -> str:  # TODO: revive func
        pass
