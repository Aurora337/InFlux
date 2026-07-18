from __future__ import annotations

from dataclasses import dataclass, field

from .replication_message import ReplicationMessage


@dataclass(slots=True)
class ReplicationQueue:
    """
    Deterministic replication queue.
    """

    _messages: list[ReplicationMessage] = field(
        default_factory=list
    )

    def enqueue(
        self,
        message: ReplicationMessage,
    ) -> bool:
        """
        Add a replication message.
        """

        self._messages.append(message)

        return True

    def dequeue(
        self,
    ) -> ReplicationMessage | None:
        """
        Remove the next message.
        """

        if not self._messages:
            return None

        return self._messages.pop(0)

    def size(
        self,
    ) -> int:
        """
        Queue size.
        """

        return len(self._messages)

    def empty(
        self,
    ) -> bool:
        """
        True if queue contains no messages.
        """

        return not self._messages

    def clear(
        self,
    ) -> None:
        """
        Clear queue.
        """

        self._messages.clear()