from __future__ import annotations

from dataclasses import dataclass, field
from time import time


@dataclass(slots=True)
class ConsensusMessage:
    """
    Deterministic consensus message.
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
        Return deterministic snapshot.
        """

        return {
            "sender": self.sender,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }