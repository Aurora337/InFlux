from __future__ import annotations

from dataclasses import dataclass, field

from .sync_metrics import SyncMetrics
from .sync_queue import SyncQueue
from .sync_snapshot import SyncSnapshot
from .sync_validator import SyncValidator


@dataclass(slots=True)
class SyncManager:
    """
    Coordinates synchronization.
    """

    queue: SyncQueue = field(
        default_factory=SyncQueue
    )

    metrics: SyncMetrics = field(
        default_factory=SyncMetrics
    )

    validator: SyncValidator = field(
        default_factory=SyncValidator
    )

    def synchronize(
        self,
        snapshot: SyncSnapshot,
    ) -> bool:
        """
        Process a synchronization snapshot.
        """

        if not self.validator.validate(snapshot):
            self.metrics.record_failure()
            return False

        self.metrics.record_snapshot()

        return True