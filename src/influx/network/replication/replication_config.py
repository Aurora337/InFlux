from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ReplicationConfig:
    """
    Deterministic replication configuration.
    """

    max_replicas: int = 3

    timeout_seconds: float = 5.0

    retry_limit: int = 3

    def validate(
        self,
    ) -> None:
        """
        Validate replication configuration.
        """

        if self.max_replicas <= 0:
            raise ValueError(
                "max replicas must be positive"
            )

        if self.timeout_seconds <= 0:
            raise ValueError(
                "timeout must be positive"
            )

        if self.retry_limit < 0:
            raise ValueError(
                "retry limit cannot be negative"
            )