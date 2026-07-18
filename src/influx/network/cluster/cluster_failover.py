from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ClusterFailover:
    """
    Tracks failover events.
    """

    failovers: int = 0

    active: bool = False

    def trigger(self) -> None:
        self.failovers += 1
        self.active = True

    def recover(self) -> None:
        self.active = False

    def snapshot(
        self,
    ) -> dict[str, int | bool]:
        return {
            "failovers": self.failovers,
            "active": self.active,
        }