from __future__ import annotations

from dataclasses import dataclass, field

from .health import (
    HealthReport,
    HealthStatus,
)


@dataclass(slots=True)
class OperationsMonitor:
    """
    Core operations health monitor.
    """

    checks: list[HealthStatus] = field(
        default_factory=list,
    )

    def record(
        self,
        status: HealthStatus,
    ) -> None:
        """
        Record health status.
        """

        self.checks.append(
            status,
        )

    def report(
        self,
    ) -> HealthReport:
        """
        Generate health report.
        """

        return HealthReport(
            statuses=list(self.checks),
        )