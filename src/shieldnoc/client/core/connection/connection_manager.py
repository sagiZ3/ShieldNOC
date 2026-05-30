import json
import socket

from time import sleep
from PySide6.QtCore import Signal, QObject
from threading import Thread, Event
from select import select

import shieldnoc.protocol as protocol

from shieldnoc.client.core.connection.chat_manager import ChatManager
from shieldnoc.client.core.connection.vpn_manager import VPNManager
from shieldnoc.client.core.data import system_metrics
from shieldnoc.logging_config import logger
from shieldnoc.client.core.data.enums import ClientField


class ConnectionManager(QObject):
    connect_process_end = Signal(bool)
    vpn_ip_change = Signal(bool, str)

    def __init__(self):
        """ Initialize connection manager and communication components. """

        super().__init__()

        self.chat_manager = ChatManager(self.send_msg)
        self._vpn_manager = VPNManager()

        self._stop_connection_event = Event()

        self._initial_conn_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._initial_conn_sock.settimeout(1.0)

    def start_connection_process(self) -> None:
        """ Start the initial connection process in a separate thread. """

        thread = Thread(target=self._initial_connection_handler)
        thread.start()
        logger.info("===== Initial Connection Started With The Server =====")

    def _initial_connection_handler(self) -> None:
        """ Handle the initial connection and VPN setup process. """

        try:
            self._initial_conn_sock.connect((protocol.SERVER_IP, protocol.CONNECTION_PORT))
        except Exception as e:
            logger.error("Encountered with a problem trying to connect the server")
            logger.error("Failed to connect socket:", e)
            exit()

        initial_data = {
            ClientField.PUBLIC_KEY: self._vpn_manager.public_key,
            ClientField.MAC: system_metrics.get_mac_addr(),
            ClientField.OS: system_metrics.get_os(),
            ClientField.HOSTNAME: system_metrics.get_hostname()
        }

        data = {field.value: value for field, value in initial_data.items()}
        encrypted_json_str = self._encrypt_data(json.dumps(data))
        self._send_vpn_data(self._initial_conn_sock, encrypted_json_str)

        logger.info("===== Initial Data Sent To Server =====")

        try:
            valid_payload, server_payload = protocol.get_payload(self._initial_conn_sock)

            if valid_payload:
                prefix = server_payload[0]

                if prefix != protocol.MessageType.VPN.value:
                    logger.error("Problem with accepting the server's initial connection data")
                    return

                decrypted_content: dict = json.loads(self._decrypt_data(server_payload[1:]))
                server_public_key = decrypted_content["server_public_key"]
                assigned_vpn_ip = decrypted_content["assigned_vpn_ip"]

                self._vpn_manager.connect_vpn(assigned_vpn_ip, server_public_key)
                logger.info("===== You Are Now Connected To ShieldNOC's VPN =====")

                self._handle_incoming_data()

            else:
                if server_payload in (ConnectionResetError.__name__, ConnectionAbortedError.__name__):
                    return

                logger.error(f"Error with accepting the content: {server_payload}")

        except Exception as e:
            logger.error(f"Initial connection failed: {e}")

        finally:
            self._initial_conn_sock.close()

    def _handle_incoming_data(self) -> None:
        """ Handle incoming data and route messages by their protocol type. """

        sleep(2)  # letting the computer time to connect the VPN

        self._conn_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._conn_sock.settimeout(1.0)
        self._conn_sock.connect((protocol.SERVER_IP, protocol.CONNECTION_PORT))

        logger.info("===== ShieldNOC Connection Is Up and Running =====")
        self.connect_process_end.emit(True)

        is_ip_changed = False

        while not self._stop_connection_event.is_set():
            try:
                valid_payload, server_payload = protocol.get_payload(self._conn_sock)
            except socket.timeout:
                continue

            except Exception as e:
                logger.warning(f"Unexpected Error occurred: {e}")
                break

            if valid_payload:
                prefix = server_payload[0]
                content = server_payload[1:]

                if prefix == protocol.MessageType.CHAT.value:
                    self.chat_manager.handle_msg(content)
                elif prefix == protocol.MessageType.VPN.value:
                    is_ip_changed, result = self.handle_vpn_ip_change(content)
                    self.vpn_ip_change.emit(is_ip_changed, result)
                    if is_ip_changed:
                        break
                else:
                    logger.warning("Got a valid server payload with invalid prefix")

            else:
                if server_payload in (ConnectionResetError.__name__, ConnectionAbortedError.__name__):
                    break

                logger.error(f"Error with accepting the content: {server_payload}")

                try:
                    while True:
                        readable, _, _ = select([self._conn_sock], [], [], 0)
                        if not readable:
                            break
                        self._conn_sock.recv(1024)  # Attempt to empty the socket from possible garbage

                except ConnectionResetError:
                    logger.warning("Server unexpectedly closed the connection in a middle of reading data")
                    break

                except Exception as e:
                    logger.warning(f"Unexpected Error occurred while trying of empty the socket: {e} ")

        # broken | Event raised
        if is_ip_changed:
            self._conn_sock.close()
            self._handle_incoming_data()

        else:
            self._conn_sock.close()
            self._vpn_manager.disconnect_vpn()
            logger.info(">>> ShieldNOC's Session Ended - Connection Closed <<<")

    def send_msg(self, msg: str) -> None:
        """ Sends a chat message to the server. """

        protocol.send_segment(self._conn_sock, f"{protocol.MessageType.CHAT.value}{msg}")

    def get_vpn_ip(self) -> str:
        """
        Returns the VPN IP address.

        :return: VPN IP address
        """

        return self._conn_sock.getsockname()[0]

    def request_new_vpn_ip(self, requested_ip: str) -> None:
        """ Requests a new VPN IP address from the server. """
        logger.info(f"Requesting new VPN IP: {requested_ip}")
        self._send_vpn_data(self._conn_sock, requested_ip)

    def handle_vpn_ip_change(self, code_and_response: str) -> tuple[bool, str]:
        """
        Handles VPN IP change response from the server.

        :return: Tuple containing status and operation result.
        """

        return self._vpn_manager.change_ip(code_and_response)

    def end_session(self):
        """ Stops the current ShieldNOC session. """

        self._stop_connection_event.set()

    @staticmethod
    def _send_vpn_data(sock: socket.socket, data: str) -> None:
        """ Sends VPN-related data using the protocol format. """

        protocol.send_segment(sock,f"{protocol.MessageType.VPN.value}{data}")

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
        Decrypt received encrypted data.

        :return: Decrypted data string.
        """

        return data
