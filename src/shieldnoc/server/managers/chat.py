# TODO: add exit when admin close the dashboard
import socket
from datetime import datetime

import shieldnoc.protocol as protocol

from threading import Thread
from select import select
from shieldnoc.logging_config import logger

class ChatManager:
    def __init__(self):
        self._listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self._listen_sock.bind((protocol.LISTEN_EVERYONE_IP, protocol.CONNECTION_PORT))
        except Exception as e:
            logger.error("Server encountered with a problem trying to establish connection to chat")
            logger.error("Failed to bind socket: " + str(e))
            exit()

        self._listen_sock.listen()
        logger.info("===== Chat Connection is up and running =====")

        self._messages: list = []
        self._clients: dict[socket.socket: tuple[str, int]] = {}  # [socket: (ip, port)]
        # TODO: add cache ?

    def start_chat(self):
        thread = Thread(target=self._clients_acceptor)
        thread.start()
        logger.info("===== Chat is ready for accepting clients =====")

    def _clients_acceptor(self) -> None:  # TODO: check if socket is ShieldNOC client
        while True:
            client_sock, client_addr = self._listen_sock.accept()
            self._clients[client_sock] = client_addr
            self.broadcast_msg(self._wrap_system_msg(f"~{client_addr[0]} joined the ShieldNOC system~"))

            thread = Thread(target=self._handle_client, args=(client_sock,))
            thread.start()

    def _handle_client(self, client_socket) -> None:
        while True:
            try:
                valid_msg, client_msg = protocol.get_payload(client_socket)

            except ConnectionResetError:
                logger.warning("Client unexpectedly closed the connection")
                break

            except Exception as e:
                logger.warning(f"Unexpected Error occurred: {e}")
                break

            if valid_msg:
                self.broadcast_msg(self._wrap_client_msg(client_msg, client_socket))
            else:
                try:
                    logger.error(f"Error with sending the message: {client_msg}")
                    while True:
                        readable, _, _ = select([client_socket], [], [], 0)
                        if not readable:
                            break
                        client_socket.recv(1024)  # Attempt to empty the socket from possible garbage

                except ConnectionResetError:
                    logger.warning("Client unexpectedly closed the connection in a middle of reading data")
                    break

                except Exception as e:
                    logger.warning(f"Unexpected Error occurred: {e} ")

        # broken
        self._clients.pop(client_socket)
        client_socket.close()

    def broadcast_msg(self, msg) -> None:
        self._messages.append(msg)
        for client_sock in self._clients:
            protocol.send_segment(client_sock, msg)

    def _wrap_system_msg(self, msg):
        return f"[{self._timestamp()}]<span style='color:#00e5ff'>\
        [{self._timestamp()}] System: {msg}.\
        </span>"

    def _wrap_server_manager_msg(self, msg):
        return f"[{self._timestamp()}]<span style='color:#ffe100'>\
        [{self._timestamp()}] Server Manager: {msg}.\
        </span>"

    def _wrap_client_msg(self, msg, client_socket):
        return f"[{self._timestamp()}] {self._clients[client_socket][0]}: {msg}"

    @staticmethod
    def _timestamp() -> str:
        return datetime.now().strftime("%H:%M:%S")

    def get_messages_list(self):
        return self._messages
