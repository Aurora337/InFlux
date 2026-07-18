from __future__ import annotations

from dataclasses import dataclass, field
import uuid


@dataclass(slots=True)
class Route:
    """
    Deterministic network route.

    Represents a validated path used by the routing subsystem.
    """

    destination: str

    route_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    cost: int = 1

    latency_score: float = 0.0

    hop_count: int = 0

    active: bool = True


    def validate(
        self,
    ) -> bool:
        """
        Validate route integrity.
        """

        if not self.destination:
            return False

        if not self.route_id:
            return False

        if self.cost < 0:
            return False

        if self.latency_score < 0:
            return False

        if self.hop_count < 0:
            return False

        return True


    def add_hop(
        self,
    ) -> bool:
        """
        Increase hop count.
        """

        self.hop_count += 1

        return True


    def deactivate(
        self,
    ) -> bool:
        """
        Disable route.
        """

        self.active = False

        return True


    def activate(
        self,
    ) -> bool:
        """
        Enable route.
        """

        self.active = True

        return True


    def snapshot(
        self,
    ) -> dict[str, object]:
        """
        Deterministic route snapshot.
        """

        return {
            "route_id": self.route_id,
            "destination": self.destination,
            "cost": self.cost,
            "latency_score": self.latency_score,
            "hop_count": self.hop_count,
            "active": self.active,
        }