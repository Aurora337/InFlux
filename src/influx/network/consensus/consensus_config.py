from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ConsensusConfig:
    """
    Consensus configuration.
    """

    quorum_size: int = 1

    timeout_seconds: float = 5.0

    max_rounds: int = 10

    def validate(self) -> None:
        """
        Validate configuration.
        """

        if self.quorum_size <= 0:
            raise ValueError(
                "quorum_size must be positive"
            )

        if self.timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be positive"
            )

        if self.max_rounds <= 0:
            raise ValueError(
                "max_rounds must be positive"
            )