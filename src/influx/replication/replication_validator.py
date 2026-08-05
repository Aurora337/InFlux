from __future__ import annotations

from .checkpoint import Checkpoint
from .replication_policy import ReplicationPolicy
from .replication_session import ReplicationSession


class ReplicationValidator:
    """
    Validates replication sessions.
    """

    def __init__(
        self,
        policy: ReplicationPolicy | None = None,
    ) -> None:

        self.policy = (
            policy
            if policy is not None
            else ReplicationPolicy()
        )

    def validate_checkpoint(
        self,
        checkpoint: Checkpoint,
    ) -> bool:
        """
        Validate checkpoint integrity.
        """

        if not checkpoint.checkpoint_id:
            return False

        if checkpoint.height < 0:
            return False

        if not checkpoint.state_hash:
            return False

        return True

    def validate_session(
        self,
        session: ReplicationSession,
    ) -> bool:
        """
        Validate replication session.
        """

        if not session.session_id:
            return False

        if not session.source_node:
            return False

        if not session.target_node:
            return False

        if session.source_node == session.target_node:
            return False

        if (
            self.policy.require_checkpoint_validation
            and not self.validate_checkpoint(
                session.checkpoint
            )
        ):
            return False

        return True

    def validate_policy(
        self,
        active_sessions: int,
    ) -> bool:
        """
        Validate concurrency policy.
        """

        return (
            active_sessions
            < self.policy.max_concurrent_sessions
        )