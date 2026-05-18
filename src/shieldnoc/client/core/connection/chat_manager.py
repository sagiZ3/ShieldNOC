class ChatManager:
    def __init__(self, send_msg_callback):
        """ Initialize chat manager and message queue. """

        self.send_msg = send_msg_callback
        self._messages: list = []

    def _add_msg_to_queue(self, msg: str):
        """ Add a new message to the queue. """

        self._messages.append(msg)

    def handle_msg(self, msg: str):
        """ Handle an incoming chat message. """

        self._add_msg_to_queue(msg)

    def get_next_msg(self) -> str | None:
        """
        Retrieve the next message from the queue.

        :return: Next queued message or None if the queue is empty.
        """

        if self._messages:
            return self._messages.pop(0)
        return None
