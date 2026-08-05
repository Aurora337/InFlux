from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SyncConfig:
    """
    Deterministic synchronization configuration.
    """

    timeout_seconds: float = 10.0

    max_retries: int = 3

    max_peers: int = 32

    def validate(
        self,
    ) -> None:
        """
        Validate synchronization configuration.
        """

        if self.timeout_seconds <= 0:
            raise ValueError(
                "timeout must be positive"
            )

        if self.max_retries < 0:
            raise ValueError(
                "max retries cannot be negative"
            )

        if self.max_peers <= 0:
            raise ValueError(
                "max peers must be positive"
            )