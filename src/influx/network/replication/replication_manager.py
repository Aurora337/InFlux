from __future__ import annotations

from dataclasses import dataclass, field

from .replication import Replication
from .replication_metrics import ReplicationMetrics
from .replication_validator import ReplicationValidator


@dataclass(slots=True)
class ReplicationManager:
    """
    Coordinates deterministic replication.
    """

    validator: ReplicationValidator = field(
        default_factory=ReplicationValidator
    )

    metrics: ReplicationMetrics = field(
        default_factory=ReplicationMetrics
    )

    def begin(
        self,
        replication: Replication,
    ) -> bool:
        """
        Begin replication.
        """

        if not self.validator.validate(replication):
            self.metrics.tasks_failed += 1
            return False

        replication.queue()
        replication.start()

        self.metrics.tasks_started += 1

        return True

    def complete(
        self,
        replication: Replication,
        replicas_written: int,
    ) -> bool:
        """
        Complete replication.
        """

        replication.complete(replicas_written)

        self.metrics.tasks_completed += 1
        self.metrics.replicas_written += replicas_written

        return True