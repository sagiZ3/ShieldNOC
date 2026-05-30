import socket
import json

from threading import Thread
from select import select
from time import sleep

import shieldnoc.protocol as protocol

from shieldnoc.logging_config import logger
from shieldnoc.server.core.connection.chat_manager import ChatManager
from shieldnoc.server.core.connection.vpn_manager import VPNManager
from shieldnoc.server.core.db.enums import ClientField
from shieldnoc.server.core.db.queries import DatabaseQueries


class ConnectionManager:
    def __init__(self, db: DatabaseQueries):
        """ Initializes the server connection manager and VPN services. """

        self._db = db
        self.chat_manager = ChatManager(self.broadcast_msg)
        self._vpn_manager = VPNManager(self._db)

        self._vpn_manager.start_vpn()

        self._stop_connection_event = self.chat_manager.stop_connection_event

        self._listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listen_sock.settimeout(1.0)

        self._listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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
        """ Starts the client connection acceptor thread. """

        thread = Thread(target=self._clients_acceptor)
        thread.start()
        logger.info("===== ShieldNOC is ready for accepting clients =====")

    def _clients_acceptor(self) -> None:
        """ Accepts incoming client connections and routes them by connection type. """

        self.chat_manager.handle_system_msg("~ShieldNOC chat system is up and running~")

        while not self._stop_connection_event.is_set():
            try:
                client_sock, client_addr = self._listen_sock.accept()
            except socket.timeout:
                continue

            if self._vpn_manager.is_valid_vpn_ip(client_addr[0]):
                thread = Thread(target=self._handle_client, args=(client_sock,))
                client_sock.settimeout(1.0)
                self._clients[client_sock] = client_addr
            else:
                thread = Thread(target=self._initial_connection, args=(client_sock,))
                client_sock.settimeout(5.0)
            thread.start()

        self._vpn_manager.stop_vpn()
        logger.info(">>> ShieldNOC System Closed <<<")

    def _initial_connection(self, client_sock: socket.socket) -> None:
        """ Handles the initial VPN setup connection with a client. """

        client_addr = client_sock.getpeername()
        logger.info(f"{client_addr} starts the connection process to ShieldNOC System")

        try:
            valid_payload, client_payload = protocol.get_payload(client_sock)

            if valid_payload:
                prefix = client_payload[0]

                if prefix != protocol.MessageType.VPN.value:
                    self.send_vpn_data(client_sock, "Initial connection must start with VPN request")
                    return

                decrypted_content: dict = json.loads(self._decrypt_data(client_payload[1:]))  # ClientField
                initial_data = {ClientField(field): value for field, value in decrypted_content.items()}  # converts ClientField values back

                server_public_key, client_assigned_vpn_ip = self._vpn_manager.add_peer(initial_data)

                if server_public_key is None:
                    logger.warning(f"client {client_addr} tries to connect ShieldNOC using invalid pubic key")
                    response = "Invalid Public Key!\nPlease try again later."
                    self.send_vpn_data(client_sock, response)
                    return

                vpn_conf_data = {
                    "server_public_key": server_public_key,
                    "assigned_vpn_ip": client_assigned_vpn_ip
                }
                data = self._encrypt_data(json.dumps(vpn_conf_data))
                self.send_vpn_data(client_sock, data)

            else:
                if client_payload in (ConnectionResetError.__name__, ConnectionAbortedError.__name__):
                    return

                logger.error(f"Error with sending the content: {client_payload}")

        except Exception as e:
            logger.error(f"Initial connection failed: {e}")

        finally:
            client_sock.close()

    def _handle_client(self, client_sock: socket.socket) -> None:
        """ Handles incoming messages and requests from a connected client. """

        client_addr = client_sock.getpeername()
        client_ip = client_addr[0]

        logger.info(f"{client_addr} has connected to ShieldNOC System")
        self.chat_manager.handle_system_msg(f"~{client_ip} joined the ShieldNOC System~")

        is_ip_changed = False

        while not self._stop_connection_event.is_set():
            try:
                valid_payload, client_payload = protocol.get_payload(client_sock)
            except socket.timeout:
                continue

            except Exception as e:
                logger.warning(f"Unexpected Error occurred: {e}")
                break

            if valid_payload:
                prefix = client_payload[0]
                content = client_payload[1:]

                if prefix == protocol.MessageType.CHAT.value:
                    self.chat_manager.handle_client_msg(client_ip, content)
                elif prefix == protocol.MessageType.VPN.value:
                    is_ip_changed, response = self._vpn_manager.handle_peer_ip_change(content)
                    formatted_response = f"{str(int(is_ip_changed))}{response}"
                    self.send_vpn_data(client_sock, formatted_response)

                    if is_ip_changed:
                        break
                else:
                    logger.warning("Got a valid client payload with invalid prefix")

            else:
                if client_payload in (ConnectionResetError.__name__, ConnectionAbortedError.__name__):
                    break

                logger.error(f"Error with sending the content: {client_payload}")

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
        client_sock.close()
        sleep(2)  # let client previous ip interface to response and close properly

        if is_ip_changed:
            self._vpn_manager.change_peer_ip(client_ip, response)
            self.chat_manager.handle_system_msg(f"~{client_ip} changed his IP to {response}~")
        elif not self._stop_connection_event.is_set():
            self._vpn_manager.remove_peer(client_ip)
            self.chat_manager.handle_system_msg(f"~{client_ip} left the ShieldNOC System~")

        logger.info(f"> ShieldNOC System End Session With Client {client_addr} <")

    def broadcast_msg(self, msg) -> None:
        """ Broadcasts a chat message to all connected clients. """

        for client_sock in self._clients:
            protocol.send_segment(client_sock, f"{protocol.MessageType.CHAT.value}{msg}")

    @staticmethod
    def send_vpn_data(client_sock, data) -> None:
        """ Sends VPN-related data using the protocol format. """

        protocol.send_segment(client_sock, f"{protocol.MessageType.VPN.value}{data}")

    @staticmethod
    def _encrypt_data(data: str) -> str:  # TODO: revive func
        """
        Encrypts sensitive data before transmission.

        :return: Encrypted data string.
        """

        return data

    @staticmethod
    def _decrypt_data(data: str) -> str:  # TODO: revive func
        """
        Decrypts received encrypted data.

        :return: Decrypted data string.
        """

        return data
