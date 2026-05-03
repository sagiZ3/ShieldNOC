class ChatManager:
    def __init__(self, send_msg_callback):
        self.send_msg = send_msg_callback
        self._messages: list = []

    def _add_msg_to_queue(self, msg: str):
        self._messages.append(msg)

    def handle_msg(self, msg):
        self._add_msg_to_queue(msg)

    def get_next_msg(self) -> str | None:
        if self._messages:
            return self._messages.pop(0)
        return None
