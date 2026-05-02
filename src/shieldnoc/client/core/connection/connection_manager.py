# TODO: add exit when client closes the dashboard
import json
import socket

import shieldnoc.protocol as protocol

from threading import Thread
from select import select

from shieldnoc.client.core.connection.chat_manager import ChatManager
from shieldnoc.client.core.connection.vpn_manager import VPNManager
from shieldnoc.client.core.data import system_metrics
from shieldnoc.logging_config import logger
from shieldnoc.client.core.data.enums import ClientField


class ConnectionManager:
    def __init__(self):
        self.chat_manager = ChatManager(self.send_msg)
        self._vpn_manager = VPNManager()

        self._stop_connection_event = self.chat_manager.stop_connection_event

        self._initial_conn_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._initial_conn_sock.settimeout(1.0)

        try:
            self._initial_conn_sock.connect((protocol.SERVER_IP, protocol.CONNECTION_PORT))
        except Exception as e:
            logger.error("Encountered with a problem trying to connect server's chat")
            logger.error("Failed to connect socket: " + str(e))
            exit()

        self._conn_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._conn_sock.settimeout(1.0)

    def start_connection(self) -> None:
        thread = Thread(target=self._initial_connection_handler)
        thread.start()
        logger.info("===== Initial Connection Started With The Server =====")

    def _initial_connection_handler(self) -> None:
        initial_data = {
            ClientField.PUBLIC_KEY: self._vpn_manager.public_key,
            ClientField.MAC: system_metrics.get_mac_addr(),
            ClientField.HOST: system_metrics.get_host(),
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

                decrypted_content: dict = self._decrypt_data(json.loads(server_payload[1:]))
                server_public_key = decrypted_content["server_public_key"]
                assigned_vpn_ip = decrypted_content["assigned_vpn_ip"]

                self._vpn_manager.connect_vpn(assigned_vpn_ip, server_public_key)
                logger.info("===== You Are Now Connected To ShieldNOC's VPN =====")

                self._handle_incoming_data()

            else:
                logger.error(f"Error with sending the content: {server_payload}")
                if server_payload in (ConnectionResetError.__name__, ConnectionAbortedError.__name__):
                    return

        except Exception as e:
            logger.error(f"Initial connection failed: {e}")

        finally:
            self._initial_conn_sock.close()

    def _handle_incoming_data(self) -> None:
        logger.info("===== Chat Connection Is Up and Running =====")

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
                    self._vpn_manager.change_ip(content)  # TODO: integrates with GUI
                else:
                    logger.warning("Got a valid server payload with invalid prefix")

            else:
                logger.error(f"Error with sending the content: {server_payload}")

                if server_payload in (ConnectionResetError.__name__, ConnectionAbortedError.__name__):
                    break

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
        self._conn_sock.close()
        self._vpn_manager.disconnect_vpn()
        logger.info(">>> ShieldNOC's Session Ended - Connection Closed <<<")

    def send_msg(self, msg) -> None:
        protocol.send_segment(self._conn_sock, msg)

    @staticmethod
    def _send_vpn_data(sock, data) -> None:
        protocol.send_segment(sock,f"{protocol.MessageType.VPN.value}{data}")

    @staticmethod
    def _encrypt_data(data: str) -> str:  # TODO: revive func
        return data

    @staticmethod
    def _decrypt_data(data: str) -> str:  # TODO: revive func
        return data
