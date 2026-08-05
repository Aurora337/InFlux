from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class AlertSeverity(str, Enum):
    """
    Supported alert severities.
    """

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class Alert:
    """
    Immutable operational alert.
    """

    component_id: str
    severity: AlertSeverity
    message: str


@dataclass(slots=True)
class AlertManager:
    """
    Collects operational alerts.
    """

    alerts: list[Alert] = field(default_factory=list)

    def add(self, alert: Alert) -> None:
        self.alerts.append(alert)

    def count(self) -> int:
        return len(self.alerts)

    def by_severity(
        self,
        severity: AlertSeverity,
    ) -> list[Alert]:
        return [
            alert
            for alert in self.alerts
            if alert.severity == severity
        ]