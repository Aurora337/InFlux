from __future__ import annotations

from dataclasses import dataclass

from .replication import Replication


@dataclass(slots=True)
class ReplicationValidator:
    """
    Validates replication tasks.
    """

    def validate(
        self,
        replication: Replication,
    ) -> bool:
        """
        Validate replication configuration.
        """

        try:
            replication.config.validate()
        except ValueError:
            return False

        return True