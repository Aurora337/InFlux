"""
Deterministic, replayable event queue for the InFlux protocol.

Provides ordered event storage with full replay capability
and chain integrity verification.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Optional, Sequence

from .event import Event, create_event, EventType


@dataclass(slots=True)
class EventQueue:
    """
    Deterministic, replayable event queue.

    Events are stored in order with chain integrity.
    The queue supports:
    - Ordered event storage
    - Full replay from any point
    - Chain integrity verification
    - Deterministic snapshots
    - Filtered event retrieval
    """

    _events: list[Event] = field(default_factory=list)
    _sequence_counter: int = 0
    _block_events: dict[int, list[str]] = field(default_factory=dict)
    _event_index: dict[str, int] = field(default_factory=dict)

    def push(
        self,
        event_type: EventType,
        source: str,
        payload: dict[str, Any],
        block_height: int,
        timestamp: Optional[int] = None,
    ) -> Event:
        """
        Push a new event onto the queue.

        Automatically sets sequence number and links to previous event.

        Args:
            event_type: The canonical event type
            source: The subsystem emitting the event
            payload: The event data
            block_height: The block height at which the event occurred
            timestamp: Unix timestamp (defaults to current time)

        Returns:
            The created Event
        """
        previous_hash = self._events[-1].hash if self._events else ""

        event = create_event(
            event_type=event_type,
            source=source,
            payload=payload,
            block_height=block_height,
            timestamp=timestamp,
            sequence=self._sequence_counter,
            previous_hash=previous_hash,
        )

        self._events.append(event)
        self._event_index[event.event_id] = len(self._events) - 1

        # Track by block
        if block_height not in self._block_events:
            self._block_events[block_height] = []
        self._block_events[block_height].append(event.event_id)

        self._sequence_counter += 1

        return event

    def push_event(self, event: Event) -> bool:
        """
        Push an externally created event onto the queue.

        The event must have the correct sequence and previous_hash.

        Args:
            event: The event to push

        Returns:
            True if the event was accepted
        """
        expected_sequence = self._sequence_counter
        expected_previous = self._events[-1].hash if self._events else ""

        if event.sequence != expected_sequence:
            return False
        if event.previous_hash != expected_previous:
            return False

        self._events.append(event)
        self._event_index[event.event_id] = len(self._events) - 1

        if event.block_height not in self._block_events:
            self._block_events[event.block_height] = []
        self._block_events[event.block_height].append(event.event_id)

        self._sequence_counter += 1
        return True

    def replay(
        self,
        start_index: int = 0,
        end_index: Optional[int] = None,
    ) -> list[Event]:
        """
        Replay events from the queue.

        Args:
            start_index: Starting index (inclusive, default: 0)
            end_index: Ending index (exclusive, default: end of queue)

        Returns:
            List of events in order
        """
        if end_index is None:
            end_index = len(self._events)
        return list(self._events[start_index:end_index])

    def replay_by_block(self, block_height: int) -> list[Event]:
        """
        Replay all events for a specific block.

        Args:
            block_height: The block to replay

        Returns:
            List of events in order for the given block
        """
        event_ids = self._block_events.get(block_height, [])
        return [self._events[self._event_index[eid]] for eid in event_ids]

    def get_event(self, event_id: str) -> Optional[Event]:
        """Get a specific event by its ID."""
        if event_id not in self._event_index:
            return None
        return self._events[self._event_index[event_id]]

    def get_events_by_type(self, event_type: EventType) -> list[Event]:
        """Get all events of a specific type."""
        return [e for e in self._events if e.event_type == event_type]

    def get_events_by_source(self, source: str) -> list[Event]:
        """Get all events from a specific source."""
        return [e for e in self._events if e.source == source]

    def get_block_heights(self) -> list[int]:
        """Get all block heights with events."""
        return sorted(self._block_events.keys())

    def event_count(self) -> int:
        """Get the total number of events in the queue."""
        return len(self._events)

    def verify_integrity(self) -> bool:
        """
        Verify the integrity of the entire event chain.

        Checks:
        - Each event's hash is valid
        - Each event's previous_hash matches the preceding event
        - Sequence numbers are monotonically increasing

        Returns:
            True if the entire chain is valid
        """
        for i, event in enumerate(self._events):
            if not event.verify():
                return False

            if i > 0:
                if event.previous_hash != self._events[i - 1].hash:
                    return False

            if event.sequence != i:
                return False

        return True

    def verify_block_integrity(self, block_height: int) -> bool:
        """
        Verify the integrity of events for a specific block.

        Args:
            block_height: The block to verify

        Returns:
            True if the block's events are valid
        """
        events = self.replay_by_block(block_height)
        for event in events:
            if not event.verify():
                return False
        return True

    def compute_root_hash(self) -> str:
        """
        Compute the root hash of the event chain.

        The root hash is the hash of the first event.

        Returns:
            Root hash (empty string if queue is empty)
        """
        return self._events[0].hash if self._events else ""

    def compute_tip_hash(self) -> str:
        """
        Compute the tip hash of the event chain.

        The tip hash is the hash of the last event.

        Returns:
            Tip hash (empty string if queue is empty)
        """
        return self._events[-1].hash if self._events else ""

    def compute_block_hash(self, block_height: int) -> str:
        """
        Compute the combined hash of all events in a block.

        Args:
            block_height: The block to compute the hash for

        Returns:
            SHA-256 hash of all event hashes concatenated
        """
        events = self.replay_by_block(block_height)
        if not events:
            return ""

        combined = "".join(e.hash for e in events)
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    def snapshot(self) -> dict[str, Any]:
        """Deterministic queue snapshot."""
        return {
            "event_count": self.event_count(),
            "sequence_counter": self._sequence_counter,
            "block_count": len(self._block_events),
            "root_hash": self.compute_root_hash(),
            "tip_hash": self.compute_tip_hash(),
            "events": [e.snapshot() for e in self._events],
        }

    def reset(self) -> None:
        """Reset the queue to empty state."""
        self._events.clear()
        self._sequence_counter = 0
        self._block_events.clear()
        self._event_index.clear()
