from __future__ import annotations


class NetworkMetrics:
    """
    Runtime network statistics.
    """

    def __init__(self) -> None:
        self.messages_sent = 0
        self.messages_received = 0
        self.sessions_open = 0

    def sent(self) -> None:
        self.messages_sent += 1

    def received(self) -> None:
        self.messages_received += 1

    def opened(self) -> None:
        self.sessions_open += 1

    def closed(self) -> None:
        self.sessions_open -= 1