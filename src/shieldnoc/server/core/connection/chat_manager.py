from threading import Event
from datetime import datetime
from html import escape


class ChatManager:
    def __init__(self, broadcast_callback):
        """ Initializes the server chat manager and message queue. """

        self._broadcast = broadcast_callback
        self._messages: list = []
        self.stop_connection_event = Event()

    def handle_client_msg(self, ip: str, msg: str) -> None:
        """ Handles and broadcasts a client chat message. """

        msg = self._get_escaped_msg(msg)
        wrapped = self._wrap_client_msg(msg, ip)
        self._add_msg_to_queue(wrapped)
        self._broadcast(wrapped)

    def handle_server_msg(self, msg: str):
        """ Handles and broadcasts a server manager message. """

        wrapped = self._wrap_server_manager_msg(msg)
        self._add_msg_to_queue(wrapped)
        self._broadcast(wrapped)

    def handle_system_msg(self, msg: str):
        """ Handles and broadcasts a system message. """

        wrapped = self._wrap_system_msg(msg)
        self._add_msg_to_queue(wrapped)
        self._broadcast(wrapped)

    def _wrap_system_msg(self, msg: str) -> str:
        """
        Wraps a system message with timestamp and HTML styling.

        :return: Formatted system message.
        """

        return f"<span style='color:#00e5ff'>[{self._timestamp()}] System:</span> {msg}"

    def _wrap_server_manager_msg(self, msg: str) -> str:
        """
        Wraps a server manager message with timestamp and HTML styling.

        :return: Formatted server manager message.
        """

        return f"<span style='color:#ffe100'>[{self._timestamp()}] Server Manager:</span> {msg}"

    def _wrap_client_msg(self, msg: str, ip: str) -> str:
        """
        Wraps a client message with timestamp and client IP.

        :return: Formatted client message.
        """

        return f"<span style='color:#66f2ac'>[{self._timestamp()}] {ip}:</span> {msg}"

    def _add_msg_to_queue(self, msg: str):
        """ Adds a new message to the queue. """

        self._messages.append(msg)

    def get_next_msg(self) -> str | None:
        """
        Retrieves the next message from the queue.

        :return: Next queued message or None if the queue is empty.
        """

        if self._messages:
            return self._messages.pop(0)
        return None

    def end_chat_session(self):
        """ Stops the current chat session. """

        self.stop_connection_event.set()

    @staticmethod
    def _get_escaped_msg(msg: str) -> str:
        """
        Escapes HTML-sensitive characters in a message.

        :return: Escaped message string.
        """

        return escape(msg)

    @staticmethod
    def _timestamp() -> str:
        """
        Generates the current chat timestamp.

        :return: Current time formatted as HH:MM:SS.
        """

        return datetime.now().strftime("%H:%M:%S")
