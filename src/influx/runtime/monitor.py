from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .metrics import RuntimeMetrics


@dataclass(slots=True)
class RuntimeMonitor:
    """
    Runtime monitoring service.

    Collects execution statistics and maintains
    deterministic runtime metrics.
    """

    metrics: RuntimeMetrics = field(default_factory=RuntimeMetrics)
    running: bool = False

    def start(self) -> None:
        """
        Start monitoring.
        """
        self.running = True

    def stop(self) -> None:
        """
        Stop monitoring.
        """
        self.running = False

    def record(self, receipt: Any) -> None:
        """
        Record an execution receipt.
        """
        self.metrics.record_execution()

    def record_dispatch(self) -> None:
        """
        Record a dispatched task.
        """
        self.metrics.record_dispatch()

    def record_failure(self) -> None:
        """
        Record a failed task.
        """
        self.metrics.record_failure()

    def reset(self) -> None:
        """
        Reset runtime statistics.
        """
        self.metrics.reset()