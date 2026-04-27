from threading import Event
from datetime import datetime
from html import escape


class ChatManager:
    def __init__(self, broadcast_callback):
        self._broadcast = broadcast_callback
        self._messages: list = []
        self.stop_connection_event = Event()

    def handle_client_msg(self, ip: str, msg: str) -> None:
        msg = self._get_escaped_msg(msg)
        wrapped = self._wrap_client_msg(msg, ip)
        self._add_msg_to_queue(wrapped)
        self._broadcast(wrapped)

    def handle_server_msg(self, msg: str):
        wrapped = self._wrap_server_manager_msg(msg)
        self._add_msg_to_queue(wrapped)
        self._broadcast(wrapped)

    def handle_system_msg(self, msg: str):
        wrapped = self._wrap_system_msg(msg)
        self._add_msg_to_queue(wrapped)
        self._broadcast(wrapped)

    def _wrap_system_msg(self, msg) -> str:
        return f"[{self._timestamp()}] <span style='color:#00e5ff'>System:</span> {msg}"

    def _wrap_server_manager_msg(self, msg) -> str:
        return f"[{self._timestamp()}] <span style='color:#ffe100'>Server Manager:</span> {msg}"

    def _wrap_client_msg(self, msg, ip: str) -> str:
        return f"[{self._timestamp()}] {ip}: {msg}"

    def _add_msg_to_queue(self, msg: str):
        self._messages.append(msg)

    def get_next_msg(self) -> str | None:
        if self._messages:
            return self._messages.pop(0)
        return None

    def end_chat_session(self):
        self.stop_connection_event.set()

    @staticmethod
    def _get_escaped_msg(msg: str) -> str:
        return escape(msg)

    @staticmethod
    def _timestamp() -> str:
        return datetime.now().strftime("%H:%M:%S")
