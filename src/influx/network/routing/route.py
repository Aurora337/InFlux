from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Any


@dataclass(slots=True)
class Route:
    """
    Represents a deterministic route between two nodes.

    Routes are immutable identifiers describing how a message
    should traverse the network. They intentionally contain no
    transport logic.
    """

    route_id: str

    source: str

    destination: str

    next_hop: str

    hop_count: int = 1

    metric: int = 1

    active: bool = True

    created_at: float = field(default_factory=time)

    updated_at: float = field(default_factory=time)

    metadata: dict[str, Any] = field(default_factory=dict)


    def touch(self) -> None:
        """
        Refresh the route timestamp after a successful update.
        """

        self.updated_at = time()


    def increment_hop(self) -> None:
        """
        Increase hop count deterministically.
        """

        self.hop_count += 1

        self.touch()


    def deactivate(self) -> None:
        """
        Mark the route as inactive.
        """

        self.active = False

        self.touch()


    def activate(self) -> None:
        """
        Reactivate the route.
        """

        self.active = True

        self.touch()


    def update_metric(self, metric: int) -> None:
        """
        Update routing metric.

        Raises
        ------
        ValueError
            If metric is negative.
        """

        if metric < 0:
            raise ValueError(
                "Routing metric cannot be negative."
            )

        self.metric = metric

        self.touch()


    def snapshot(self) -> dict[str, Any]:
        """
        Produce a deterministic route snapshot.
        """

        return {
            "route_id": self.route_id,
            "source": self.source,
            "destination": self.destination,
            "next_hop": self.next_hop,
            "hop_count": self.hop_count,
            "metric": self.metric,
            "active": self.active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": dict(self.metadata),
        }