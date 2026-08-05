from __future__ import annotations

from collections import deque
from typing import Deque, Optional

from .message import Message


class MessageQueue:
    """
    FIFO deterministic message queue.

    All routing components exchange messages through
    this queue to preserve deterministic ordering.
    """

    def __init__(self) -> None:
        self._queue: Deque[
            Message
        ] = deque()


    def enqueue(
        self,
        message: Message,
    ) -> None:
        """
        Insert a message.
        """

        self._queue.append(
            message
        )


    def dequeue(self) -> Optional[Message]:
        """
        Remove the oldest message.
        """

        if not self._queue:
            return None

        return self._queue.popleft()


    def peek(self) -> Optional[Message]:
        """
        Inspect the next message.
        """

        if not self._queue:
            return None

        return self._queue[0]


    def clear(self) -> None:
        """
        Remove every queued message.
        """

        self._queue.clear()


    def empty(self) -> bool:
        """
        Determine whether the queue is empty.
        """

        return len(
            self._queue
        ) == 0


    def size(self) -> int:
        """
        Current queue size.
        """

        return len(
            self._queue
        )


    def snapshot(self) -> list[dict]:
        """
        Deterministic queue snapshot.
        """

        return [
            message.snapshot()
            for message
            in self._queue
        ]