from __future__ import annotations

from dataclasses import dataclass, field
from time import time


@dataclass(slots=True)
class ReplicationMessage:
    """
    Deterministic replication message.
    """

    sender: str

    payload: str

    timestamp: float = field(
        default_factory=time
    )

    def snapshot(
        self,
    ) -> dict[str, str | float]:
        """
        Deterministic message snapshot.
        """

        return {
            "sender": self.sender,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }