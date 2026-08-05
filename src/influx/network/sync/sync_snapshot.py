from __future__ import annotations

from dataclasses import dataclass, field
from time import time


@dataclass(slots=True)
class SyncSnapshot:
    """
    Deterministic synchronization snapshot.
    """

    snapshot_id: str

    height: int

    state_hash: str

    created_at: float = field(
        default_factory=time
    )

    def snapshot(
        self,
    ) -> dict[str, str | int | float]:
        """
        Return snapshot metadata.
        """

        return {
            "snapshot_id": self.snapshot_id,
            "height": self.height,
            "state_hash": self.state_hash,
            "created_at": self.created_at,
        }