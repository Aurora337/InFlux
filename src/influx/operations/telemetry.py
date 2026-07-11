from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class TelemetryEvent:
    """
    Deterministic operational telemetry event.
    """

    event_type: str

    source_id: str

    payload: dict[str, Any]


@dataclass(slots=True)
class TelemetryCollector:
    """
    Collects operational events.
    """

    events: list[TelemetryEvent] = field(
        default_factory=list,
    )

    def record(
        self,
        event: TelemetryEvent,
    ) -> None:
        """
        Store telemetry event.
        """

        self.events.append(
            event,
        )

    def count(
        self,
    ) -> int:
        """
        Return collected event count.
        """

        return len(self.events)

    def events_by_type(
        self,
        event_type: str,
    ) -> list[TelemetryEvent]:
        """
        Filter telemetry by event type.
        """

        return [
            event
            for event in self.events
            if event.event_type == event_type
        ]