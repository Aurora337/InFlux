from __future__ import annotations

from dataclasses import dataclass, field
from time import time


@dataclass(slots=True, frozen=True)
class Checkpoint:
    """
    Immutable ledger checkpoint used during deterministic replication.
    """

    checkpoint_id: str

    height: int

    state_hash: str

    timestamp: float = field(default_factory=time)

    def snapshot(self) -> dict:
        """
        Deterministic checkpoint snapshot.
        """

        return {
            "checkpoint_id": self.checkpoint_id,
            "height": self.height,
            "state_hash": self.state_hash,
            "timestamp": self.timestamp,
        }