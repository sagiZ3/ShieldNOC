import socket

import shieldnoc.protocol as protocol

from threading import Thread, Event
from select import select
from shieldnoc.logging_config import logger
from shieldnoc.server.managers.connections.chat_manager import ChatManager


class ConnectionManager:
    CHAT_PREFIX = "0"
    VPN_PREFIX = "3"

    def __init__(self):
        self._chat_manager = ChatManager(self.broadcast_msg)
        # self.vpn_manager = VPNManager()

        self._listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listen_sock.settimeout(1.0)
        self._stop_chat_event = Event()

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
        while not self._stop_chat_event.is_set():
            try:
                client_sock, client_addr = self._listen_sock.accept()
            except socket.timeout:
                continue

            logger.info(f"{client_addr} starts the connection process to ShieldNOC System")

            thread = Thread(target=self._initial_connection, args=(client_sock,))
            thread.start()

        # TODO: fix
        client_sock.settimeout(1.0)  # before sending to handle client
        self._clients[client_sock] = client_sock.getpeername()  # before sending to handle client

        logger.info(">>> ShieldNOC System Closed <<<")

    def _initial_connection(self, client_sock: socket.socket) -> None:
        try:
            valid_msg, client_msg = protocol.get_payload(client_sock)

            if valid_msg:
                prefix = client_msg[0]

                if prefix != self.VPN_PREFIX:
                    protocol.send_segment(client_sock, "Initial connection must start with VPN request")
                    return

                content = client_msg[1:]
                # send PUB KEY to vpn_manager -> create there handle initial connection

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
        self._chat_manager.handle_system_msg(f"~{client_addr[0]} joined the ShieldNOC System~")

        while not self._stop_chat_event.is_set():
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
                    self._chat_manager.handle_client_msg(client_addr[0], content)
                elif prefix == self.VPN_PREFIX:
                    pass  # api_to_vpn_somehow
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
        # update what needs in DB
        client_sock.close()
        logger.info(f"> ShieldNOC System End Session With Client {client_addr} <")

    def end_chat_session(self):
        self._stop_chat_event.set()

    def broadcast_msg(self, msg) -> None:
        for client_sock in self._clients:
            protocol.send_segment(client_sock, "0" + msg)
