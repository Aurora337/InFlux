from __future__ import annotations

from collections import deque

from influx.network.message import NetworkMessage


class MessageQueue:
    """
    Deterministic FIFO message queue.
    """

    def __init__(self) -> None:
        self._queue: deque[NetworkMessage] = deque()

    def enqueue(self, message: NetworkMessage) -> None:
        self._queue.append(message)

    def dequeue(self) -> NetworkMessage | None:
        if not self._queue:
            return None
        return self._queue.popleft()

    def peek(self) -> NetworkMessage | None:
        if not self._queue:
            return None
        return self._queue[0]

    def size(self) -> int:
        return len(self._queue)

    def empty(self) -> bool:
        return len(self._queue) == 0