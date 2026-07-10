from __future__ import annotations

from influx.network.message import NetworkMessage
from influx.network.queue import MessageQueue


class MessageDispatcher:
    """
    Dispatches deterministic messages from the queue.
    """

    def __init__(self, queue: MessageQueue):
        self.queue = queue

    def submit(self, message: NetworkMessage) -> None:
        self.queue.enqueue(message)

    def next_message(self) -> NetworkMessage | None:
        return self.queue.dequeue()