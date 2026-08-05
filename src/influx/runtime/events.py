from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class RuntimeEvent:
    """
    Deterministic runtime event.
    """

    event_type: str
    payload: dict[str, Any]


class EventBus:
    """
    Runtime event dispatcher.

    Maintains deterministic event ordering.
    """

    def __init__(self) -> None:
        self.events: list[RuntimeEvent] = []

    def emit(
        self,
        event: RuntimeEvent,
    ) -> None:
        """
        Record a runtime event.
        """

        self.events.append(event)

    def latest(
        self,
    ) -> RuntimeEvent | None:
        """
        Return most recent event.
        """

        if not self.events:
            return None

        return self.events[-1]

    def count(
        self,
    ) -> int:
        """
        Return number of events.
        """

        return len(self.events)