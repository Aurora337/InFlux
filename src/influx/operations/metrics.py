from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class OperationsMetrics:
    """
    Aggregated operational measurements.
    """

    nodes_online: int = 0

    validators_active: int = 0

    messages_processed: int = 0

    events_recorded: int = 0

    def record_event(
        self,
    ) -> None:
        """
        Increment event counter.
        """

        self.events_recorded += 1

    def record_message(
        self,
    ) -> None:
        """
        Increment message counter.
        """

        self.messages_processed += 1

    def snapshot(
        self,
    ) -> dict[str, int]:
        """
        Return deterministic metrics snapshot.
        """

        return {
            "nodes_online": self.nodes_online,
            "validators_active": self.validators_active,
            "messages_processed": self.messages_processed,
            "events_recorded": self.events_recorded,
        }