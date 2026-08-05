from __future__ import annotations

from dataclasses import dataclass

from .alerts import AlertManager
from .health import HealthReport
from .metrics import OperationsMetrics


@dataclass(slots=True)
class DashboardSnapshot:
    """
    Immutable dashboard state.
    """

    health: HealthReport
    metrics: dict[str, int]
    alert_count: int


class OperationsDashboard:
    """
    Builds dashboard snapshots.
    """

    def snapshot(
        self,
        report: HealthReport,
        metrics: OperationsMetrics,
        alerts: AlertManager,
    ) -> DashboardSnapshot:
        return DashboardSnapshot(
            health=report,
            metrics=metrics.snapshot(),
            alert_count=alerts.count(),
        )