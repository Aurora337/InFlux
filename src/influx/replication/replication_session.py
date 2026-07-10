from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Optional

from .checkpoint import Checkpoint
from .replication_state import ReplicationState


@dataclass(slots=True)
class ReplicationSession:
    """
    Represents one deterministic replication session between two nodes.
    """

    session_id: str

    source_node: str

    target_node: str

    checkpoint: Checkpoint

    state: ReplicationState = ReplicationState.CREATED

    created_at: float = field(default_factory=time)

    completed_at: Optional[float] = None

    verified: bool = False

    def start(self) -> None:
        """
        Begin replication.
        """

        self.state = ReplicationState.SYNCING

    def verify(self) -> None:
        """
        Verify replicated state.
        """

        self.state = ReplicationState.VERIFYING
        self.verified = True

    def commit(self) -> None:
        """
        Commit replication.
        """

        self.state = ReplicationState.COMMITTED
        self.completed_at = time()

    def fail(self) -> None:
        """
        Mark replication as failed.
        """

        self.state = ReplicationState.FAILED
        self.completed_at = time()

    def cancel(self) -> None:
        """
        Cancel replication.
        """

        self.state = ReplicationState.CANCELLED
        self.completed_at = time()

    def snapshot(self) -> dict:
        """
        Deterministic session snapshot.
        """

        return {
            "session_id": self.session_id,
            "source_node": self.source_node,
            "target_node": self.target_node,
            "checkpoint": self.checkpoint.snapshot(),
            "state": self.state.value,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "verified": self.verified,
        }