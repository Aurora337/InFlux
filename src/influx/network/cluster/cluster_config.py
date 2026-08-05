from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ClusterConfig:
    """
    Deterministic cluster configuration.
    """

    max_members: int = 128

    min_members: int = 1

    def validate(self) -> None:
        """
        Validate cluster configuration.
        """

        if self.min_members <= 0:
            raise ValueError(
                "minimum members must be positive"
            )

        if self.max_members < self.min_members:
            raise ValueError(
                "maximum members below minimum"
            )