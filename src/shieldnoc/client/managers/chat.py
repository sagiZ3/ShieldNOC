# TODO: add exit when client closes the dashboard
import socket
from datetime import datetime

import shieldnoc.protocol as protocol

from threading import Thread, Event
from select import select
from shieldnoc.logging_config import logger

class ChatManager:
    def __init__(self):
        self._conn_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._conn_sock.settimeout(1.0)
        self._stop_chat_event = Event()

        try:
            self._conn_sock.connect((protocol.SERVER_IP, protocol.CONNECTION_PORT))
        except Exception as e:
            logger.error("Encountered with a problem trying to connect server's chat")
            logger.error("Failed to connect socket: " + str(e))
            exit()

        logger.info("===== Chat Connection is up and running =====")

        self._messages: list = []

    def start_chat(self):
        thread = Thread(target=self._receive_messages)
        thread.start()
        logger.info("===== Chat is up! You can chat now =====")

    def _receive_messages(self) -> None:
        while not self._stop_chat_event.is_set():
            try:
                valid_msg, msg = protocol.get_payload(self._conn_sock)
            except socket.timeout:
                continue

            except ConnectionResetError:
                logger.warning("Server unexpectedly closed the connection")
                break

            except Exception as e:
                logger.warning(f"Unexpected Error occurred: {e}")
                break

            if valid_msg:
                self._messages.append(msg)
            else:
                try:
                    logger.error(f"Error with sending the message: {msg}")
                    while True:
                        readable, _, _ = select([self._conn_sock], [], [], 0)
                        if not readable:
                            break
                        self._conn_sock.recv(1024)  # Attempt to empty the socket from possible garbage

                except ConnectionResetError:
                    logger.warning("Server unexpectedly closed the connection in a middle of reading data")
                    break

                except Exception as e:
                    logger.warning(f"Unexpected Error occurred: {e} ")

        # broken | Event raised
        self._conn_sock.close()
        logger.info(">>> Chat Connection Closed <<<")

    def send_msg(self, msg) -> None:
        protocol.send_segment(self._conn_sock, msg)

    def get_next_msg(self) -> str | None:
        if self._messages:
            return self._messages.pop(0)
        return None

    def end_chat_session(self):
        self._stop_chat_event.set()

    @staticmethod
    def _timestamp() -> str:
        return datetime.now().strftime("%H:%M:%S")
