from __future__ import annotations

from dataclasses import dataclass, field

from .network import TestnetNetwork


@dataclass(slots=True)
class TestnetSimulation:
    """
    Deterministic network simulation engine.
    """

    __test__ = False

    ...

    network: TestnetNetwork

    events: list[str] = field(
        default_factory=list,
    )

    def record_event(
        self,
        event: str,
    ) -> None:
        """
        Record simulation event.
        """

        self.events.append(
            event,
        )

    def node_count(
        self,
    ) -> int:
        """
        Return current network size.
        """

        return self.network.node_count()

    def event_count(
        self,
    ) -> int:
        """
        Return event count.
        """

        return len(self.events)