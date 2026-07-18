from __future__ import annotations

from dataclasses import dataclass, field
from time import time


@dataclass(slots=True)
class SyncSession:
    """
    Represents one synchronization session.
    """

    session_id: str

    peer_id: str

    started_at: float = field(
        default_factory=time
    )

    completed: bool = False

    def finish(
        self,
    ) -> None:
        """
        Complete synchronization session.
        """

        self.completed = True

    def snapshot(
        self,
    ) -> dict[str, str | float | bool]:
        """
        Deterministic session snapshot.
        """

        return {
            "session_id": self.session_id,
            "peer_id": self.peer_id,
            "started_at": self.started_at,
            "completed": self.completed,
        }