from __future__ import annotations

from dataclasses import dataclass, field

from .replication_config import ReplicationConfig
from .replication_result import ReplicationResult
from .replication_state import ReplicationState


@dataclass(slots=True)
class Replication:
    """
    Deterministic replication task.
    """

    replication_id: str

    config: ReplicationConfig = field(
        default_factory=ReplicationConfig
    )

    state: ReplicationState = (
        ReplicationState.INITIALIZING
    )

    target_replicas: list[str] = field(
        default_factory=list
    )

    def queue(
        self,
    ) -> bool:
        """
        Move replication into queue.
        """

        self.state = ReplicationState.QUEUED

        return True


    def start(
        self,
    ) -> bool:
        """
        Start replication.
        """

        self.state = ReplicationState.REPLICATING

        return True


    def complete(
        self,
        replicas_written: int,
    ) -> ReplicationResult:
        """
        Complete replication.
        """

        self.state = ReplicationState.SYNCHRONIZED

        return ReplicationResult(
            success=True,
            replicas_written=replicas_written,
        )


    def fail(
        self,
        error: str,
    ) -> ReplicationResult:
        """
        Fail replication.
        """

        self.state = ReplicationState.FAILED

        return ReplicationResult(
            success=False,
            error=error,
        )