from __future__ import annotations

from dataclasses import dataclass, field
from time import time


@dataclass(slots=True)
class ClusterHeartbeat:
    """
    Tracks deterministic heartbeat activity.
    """

    last_heartbeat: float = field(
        default_factory=time
    )

    heartbeat_count: int = 0

    def beat(
        self,
    ) -> None:
        """
        Record a heartbeat.
        """

        self.last_heartbeat = time()
        self.heartbeat_count += 1

    def snapshot(
        self,
    ) -> dict[str, float | int]:
        return {
            "last_heartbeat": self.last_heartbeat,
            "heartbeat_count": self.heartbeat_count,
        }