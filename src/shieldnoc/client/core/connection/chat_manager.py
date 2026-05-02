from threading import Event


class ChatManager:
    def __init__(self, send_msg_callback):
        self._send_msg = send_msg_callback
        self._messages: list = []
        self.stop_connection_event = Event()

    def _add_msg_to_queue(self, msg: str):
        self._messages.append(msg)

    def handle_msg(self, msg):
        self._add_msg_to_queue(msg)
        self._send_msg(msg)

    def get_next_msg(self) -> str | None:
        if self._messages:
            return self._messages.pop(0)
        return None

    def end_chat_session(self):
        self.stop_connection_event.set()
