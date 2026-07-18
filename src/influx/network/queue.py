from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from influx.network.message import NetworkMessage


@dataclass(slots=True)
class MessageQueue:
    """
    Deterministic FIFO queue for network messages.
    """

    _queue: deque[NetworkMessage] = field(
        default_factory=deque,
        init=False,
        repr=False,
    )

    def enqueue(
        self,
        message: NetworkMessage,
    ) -> None:
        """
        Add a message to the end of the queue.
        """

        self._queue.append(message)

    def dequeue(
        self,
    ) -> NetworkMessage | None:
        """
        Remove and return the next message.

        Returns None if the queue is empty.
        """

        if not self._queue:
            return None

        return self._queue.popleft()

    def peek(
        self,
    ) -> NetworkMessage | None:
        """
        Return the next message without removing it.
        """

        if not self._queue:
            return None

        return self._queue[0]

    def size(
        self,
    ) -> int:
        """
        Return the number of queued messages.
        """

        return len(self._queue)

    def empty(
        self,
    ) -> bool:
        """
        Return True if the queue is empty.
        """

        return len(self._queue) == 0

    def clear(
        self,
    ) -> None:
        """
        Remove all queued messages.
        """

        self._queue.clear()