from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ClusterHealth:
    """
    Deterministic cluster health information.
    """

    healthy_nodes: int = 0

    unhealthy_nodes: int = 0

    heartbeat_failures: int = 0

    def healthy(
        self,
    ) -> bool:
        """
        Overall cluster health.
        """

        return (
            self.unhealthy_nodes == 0
            and self.heartbeat_failures == 0
        )

    def snapshot(
        self,
    ) -> dict[str, int | bool]:
        return {
            "healthy_nodes": self.healthy_nodes,
            "unhealthy_nodes": self.unhealthy_nodes,
            "heartbeat_failures": self.heartbeat_failures,
            "healthy": self.healthy(),
        }