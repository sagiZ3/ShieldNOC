# TODO: add exit when admin close the dashboard
import socket
from datetime import datetime

import shieldnoc.protocol as protocol

from threading import Thread, Event
from select import select
from shieldnoc.logging_config import logger


class ChatManager:
    def __init__(self):
        self._listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listen_sock.settimeout(1.0)
        self._stop_chat_event = Event()

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

        self.broadcast_msg(self._wrap_system_msg(f"~ShieldNOC chat system is ready~"))
        # TODO: add cache ?

    def start_chat(self):
        thread = Thread(target=self._clients_acceptor)
        thread.start()
        logger.info("===== Chat is ready for accepting clients =====")

    def _clients_acceptor(self) -> None:  # TODO: check if socket is ShieldNOC client
        while not self._stop_chat_event.is_set():
            try:
                client_sock, client_addr = self._listen_sock.accept()
            except socket.timeout:
                continue

            logger.info(f"{client_addr} has connected to chat socket")

            client_sock.settimeout(1.0)
            self._clients[client_sock] = client_addr
            self.broadcast_msg(self._wrap_system_msg(f"~{client_addr[0]} joined the ShieldNOC system~"))

            thread = Thread(target=self._handle_client, args=(client_sock,))
            thread.start()

        logger.info(">>> Chat System Closed <<<")

    def _handle_client(self, client_sock: socket.socket) -> None:
        while not self._stop_chat_event.is_set():
            try:
                valid_msg, client_msg = protocol.get_payload(client_sock)
            except socket.timeout:
                continue

            except ConnectionResetError:
                logger.warning("Client unexpectedly closed the connection")
                break

            except Exception as e:
                logger.warning(f"Unexpected Error occurred: {e}")
                break

            if valid_msg:
                self.broadcast_msg(self._wrap_client_msg(client_msg, client_sock))
            else:
                try:
                    logger.error(f"Error with sending the message: {client_msg}")
                    while True:
                        readable, _, _ = select([client_sock], [], [], 0)
                        if not readable:
                            break
                        client_sock.recv(1024)  # Attempt to empty the socket from possible garbage

                except ConnectionResetError:
                    logger.warning("Client unexpectedly closed the connection in a middle of reading data")
                    break

                except Exception as e:
                    logger.warning(f"Unexpected Error occurred: {e} ")

        # broken | Event raised
        self._clients.pop(client_sock)
        logger.info(f"> Chat System End Session with client {client_sock.getpeername()} <")
        client_sock.close()

    def broadcast_msg(self, msg) -> None:
        self._messages.append(msg)
        for client_sock in self._clients:
            protocol.send_segment(client_sock, msg)

    def _wrap_system_msg(self, msg) -> str:
        return f"[{self._timestamp()}] <span style='color:#00e5ff'>System:</span> {msg}"

    def wrap_server_manager_msg(self, msg) -> str:
        return f"[{self._timestamp()}] <span style='color:#ffe100'>Server Manager:</span> {msg}"

    def _wrap_client_msg(self, msg, client_sock) -> str:
        return f"[{self._timestamp()}] {self._clients[client_sock][0]}: {msg}"

    def get_next_msg(self) -> str | None:
        if self._messages:
            return self._messages.pop(0)
        return None

    def end_chat_session(self):
        self._stop_chat_event.set()

    @staticmethod
    def _timestamp() -> str:
        return datetime.now().strftime("%H:%M:%S")
