from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4
from time import time


@dataclass(slots=True)
class SyncRequest:
    """
    Request for synchronization data.
    """

    requester: str

    target: str

    state_hash: str = ""

    request_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    timestamp: float = field(
        default_factory=time
    )

    range_start: int = 0

    range_end: int = 0


    def snapshot(self) -> dict:
        """
        Deterministic request snapshot.
        """

        return {
            "request_id":
                self.request_id,

            "requester":
                self.requester,

            "target":
                self.target,

            "state_hash":
                self.state_hash,

            "timestamp":
                self.timestamp,

            "range_start":
                self.range_start,

            "range_end":
                self.range_end,
        }