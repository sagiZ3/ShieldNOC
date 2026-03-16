import socket
import shieldnoc.protocol as protocol

from threading import Thread
from select import select
from shieldnoc.logging_config import logger

class ChatConnection:
    def __init__(self):
        self._conn_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self._conn_sock.bind((protocol.LISTEN_EVERYONE_IP, protocol.CONNECTION_PORT))
        except Exception as e:
            logger.error("Failed to bind socket: " + str(e))
            exit()

        self._conn_sock.listen()
        logger.info("===== Chat Connection is up and running =====")

        self.messages: list = []
        self._clients: dict[socket.socket: tuple[str, int]] = {}
        # TODO: add cache ?

    def clients_acceptor(self) -> None:
        while True:
            client_sock, client_addr = self._conn_sock.accept()
            self._clients[client_sock] = client_addr
            self._broadcast(f"{client_addr} joined the chat!")

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
                self._broadcast(f"{self._clients[client_socket][0]}: {client_msg}")
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

    def _broadcast(self, msg):
        self.messages.append(msg)
        for client_sock in self._clients:
            protocol.send_segment(client_sock, msg)
