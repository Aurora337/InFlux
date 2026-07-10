from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ReplicationPolicy:
    """
    Replication policy configuration.
    """

    max_concurrent_sessions: int = 8

    replication_timeout: float = 30.0

    retry_limit: int = 3

    require_trusted_source: bool = False

    require_checkpoint_validation: bool = True

    def snapshot(self) -> dict:
        """
        Deterministic policy snapshot.
        """

        return {
            "max_concurrent_sessions":
                self.max_concurrent_sessions,

            "replication_timeout":
                self.replication_timeout,

            "retry_limit":
                self.retry_limit,

            "require_trusted_source":
                self.require_trusted_source,

            "require_checkpoint_validation":
                self.require_checkpoint_validation,
        }