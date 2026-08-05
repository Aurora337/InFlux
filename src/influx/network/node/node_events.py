from __future__ import annotations

from dataclasses import dataclass, field

from .node_event import NodeEvent


@dataclass(slots=True)
class NodeEvents:
    """
    Deterministic node event log.
    """

    _events: list[NodeEvent] = field(
        default_factory=list
    )

    def record(
        self,
        event: NodeEvent,
    ) -> None:
        """
        Record a node event.
        """

        self._events.append(event)

    def events(self) -> list[NodeEvent]:
        """
        Return all recorded events.
        """

        return list(self._events)

    def count(self) -> int:
        """
        Number of recorded events.
        """

        return len(self._events)

    def clear(self) -> None:
        """
        Remove all recorded events.
        """

        self._events.clear()