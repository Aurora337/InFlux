from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ContractEvent:
    """
    Deterministic contract event.
    """

    event_name: str
    contract_id: str
    payload: dict[str, Any]


@dataclass(slots=True)
class EventEmitter:
    """
    Stores emitted contract events.
    """

    events: list[ContractEvent] = field(
        default_factory=list,
    )

    def emit(
        self,
        event: ContractEvent,
    ) -> None:
        """
        Emit an event.
        """

        self.events.append(event)

    def count(self) -> int:
        return len(self.events)

    def all_events(self) -> list[ContractEvent]:
        return list(self.events)