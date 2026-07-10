from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AttackEvent:
    """
    Represents a detected network attack.
    """

    source: str

    attack_type: str

    severity: int


class AttackMonitor:
    """
    Tracks suspicious network events.
    """

    def __init__(
        self,
    ) -> None:

        self._events: list[AttackEvent] = []

    def record(
        self,
        event: AttackEvent,
    ) -> None:
        """
        Record attack event.
        """

        self._events.append(
            event
        )

    def events(
        self,
    ) -> list[AttackEvent]:
        """
        Return recorded events.
        """

        return list(
            self._events
        )

    def count(
        self,
    ) -> int:
        """
        Return attack count.
        """

        return len(
            self._events
        )