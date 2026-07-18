from __future__ import annotations

from dataclasses import dataclass, field

from .sync_message import SyncMessage


@dataclass(slots=True)
class SyncQueue:
    """
    FIFO synchronization queue.
    """

    _messages: list[SyncMessage] = field(
        default_factory=list
    )

    def enqueue(
        self,
        message: SyncMessage,
    ) -> bool:
        """
        Add message.
        """

        self._messages.append(message)

        return True

    def dequeue(
        self,
    ) -> SyncMessage | None:
        """
        Remove next message.
        """

        if not self._messages:
            return None

        return self._messages.pop(0)

    def size(
        self,
    ) -> int:
        """
        Queue length.
        """

        return len(self._messages)

    def empty(
        self,
    ) -> bool:
        """
        Return True if queue is empty.
        """

        return not self._messages

    def clear(
        self,
    ) -> None:
        """
        Remove all queued messages.
        """

        self._messages.clear()