from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HealthStatus:
    """
    Deterministic health state.
    """

    component_id: str

    healthy: bool

    message: str = ""


@dataclass(slots=True)
class HealthReport:
    """
    Collection of component health results.
    """

    statuses: list[HealthStatus]

    def healthy_count(self) -> int:
        """
        Count healthy components.
        """

        return sum(
            1
            for status in self.statuses
            if status.healthy
        )

    def unhealthy_count(self) -> int:
        """
        Count unhealthy components.
        """

        return sum(
            1
            for status in self.statuses
            if not status.healthy
        )

    def is_healthy(self) -> bool:
        """
        Determine overall health.
        """

        return self.unhealthy_count() == 0