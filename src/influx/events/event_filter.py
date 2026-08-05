"""
Deterministic event filtering for the InFlux protocol.

Provides composable filter predicates for querying
event streams by type, source, block height, time range,
and custom predicates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from .event import Event, EventType


EventPredicate = Callable[[Event], bool]


@dataclass(slots=True)
class EventFilter:
    """
    Composable event filter for querying event streams.

    Supports filtering by:
    - Event type
    - Source subsystem
    - Block height range
    - Time range
    - Custom predicates
    - Payload field matching
    """

    event_types: Optional[set[EventType]] = None
    sources: Optional[set[str]] = None
    min_block_height: Optional[int] = None
    max_block_height: Optional[int] = None
    min_timestamp: Optional[int] = None
    max_timestamp: Optional[int] = None
    payload_filters: Optional[dict[str, Any]] = None
    custom_predicates: list[EventPredicate] = field(default_factory=list)

    def matches(self, event: Event) -> bool:
        """
        Check if an event matches all filter criteria.

        Args:
            event: The event to check

        Returns:
            True if the event matches all criteria
        """
        # Event type filter
        if self.event_types is not None and event.event_type not in self.event_types:
            return False

        # Source filter
        if self.sources is not None and event.source not in self.sources:
            return False

        # Block height range
        if self.min_block_height is not None and event.block_height < self.min_block_height:
            return False
        if self.max_block_height is not None and event.block_height > self.max_block_height:
            return False

        # Time range
        if self.min_timestamp is not None and event.timestamp < self.min_timestamp:
            return False
        if self.max_timestamp is not None and event.timestamp > self.max_timestamp:
            return False

        # Payload field matching
        if self.payload_filters is not None:
            for key, value in self.payload_filters.items():
                if key not in event.payload:
                    return False
                if event.payload[key] != value:
                    return False

        # Custom predicates
        for predicate in self.custom_predicates:
            if not predicate(event):
                return False

        return True

    def apply(self, events: list[Event]) -> list[Event]:
        """
        Apply the filter to a list of events.

        Args:
            events: List of events to filter

        Returns:
            Filtered list of events
        """
        return [e for e in events if self.matches(e)]

    def and_filter(self, other: EventFilter) -> EventFilter:
        """
        Combine this filter with another using AND logic.

        Args:
            other: Another filter to combine

        Returns:
            A new filter that matches events matching both filters
        """
        combined = EventFilter(
            custom_predicates=list(self.custom_predicates),
        )

        # Merge event types (intersection)
        if self.event_types is not None and other.event_types is not None:
            combined.event_types = self.event_types & other.event_types
        elif self.event_types is not None:
            combined.event_types = set(self.event_types)
        elif other.event_types is not None:
            combined.event_types = set(other.event_types)

        # Merge sources (intersection)
        if self.sources is not None and other.sources is not None:
            combined.sources = self.sources & other.sources
        elif self.sources is not None:
            combined.sources = set(self.sources)
        elif other.sources is not None:
            combined.sources = set(other.sources)

        # Merge block height ranges (most restrictive)
        combined.min_block_height = max(
            self.min_block_height or 0,
            other.min_block_height or 0,
        ) if (self.min_block_height is not None or other.min_block_height is not None) else None

        combined.max_block_height = min(
            self.max_block_height or 999999999,
            other.max_block_height or 999999999,
        ) if (self.max_block_height is not None or other.max_block_height is not None) else None

        # Merge time ranges (most restrictive)
        combined.min_timestamp = max(
            self.min_timestamp or 0,
            other.min_timestamp or 0,
        ) if (self.min_timestamp is not None or other.min_timestamp is not None) else None

        combined.max_timestamp = min(
            self.max_timestamp or 9999999999,
            other.max_timestamp or 9999999999,
        ) if (self.max_timestamp is not None or other.max_timestamp is not None) else None

        # Merge payload filters
        if self.payload_filters is not None and other.payload_filters is not None:
            combined.payload_filters = {**self.payload_filters, **other.payload_filters}
        elif self.payload_filters is not None:
            combined.payload_filters = dict(self.payload_filters)
        elif other.payload_filters is not None:
            combined.payload_filters = dict(other.payload_filters)

        # Combine custom predicates
        combined.custom_predicates.extend(other.custom_predicates)

        return combined

    def or_filter(self, other: EventFilter) -> EventFilter:
        """
        Combine this filter with another using OR logic.

        Args:
            other: Another filter to combine

        Returns:
            A new filter that matches events matching either filter
        """
        # Use a custom predicate for OR logic
        self_predicate = self.matches
        other_predicate = other.matches

        combined = EventFilter(
            custom_predicates=[lambda e: self_predicate(e) or other_predicate(e)],
        )
        return combined

    def negate(self) -> EventFilter:
        """
        Create a filter that matches events NOT matching this filter.

        Returns:
            A new inverted filter
        """
        self_predicate = self.matches
        return EventFilter(
            custom_predicates=[lambda e: not self_predicate(e)],
        )

    def snapshot(self) -> dict[str, Any]:
        """Deterministic filter snapshot."""
        return {
            "event_types": sorted(et.value for et in (self.event_types or set())),
            "sources": sorted(self.sources or set()),
            "min_block_height": self.min_block_height,
            "max_block_height": self.max_block_height,
            "min_timestamp": self.min_timestamp,
            "max_timestamp": self.max_timestamp,
            "payload_filters": self.payload_filters,
            "custom_predicate_count": len(self.custom_predicates),
        }


def filter_by_type(event_type: EventType) -> EventFilter:
    """Create a filter for a specific event type."""
    return EventFilter(event_types={event_type})


def filter_by_source(source: str) -> EventFilter:
    """Create a filter for a specific source subsystem."""
    return EventFilter(sources={source})


def filter_by_block_range(min_height: int, max_height: int) -> EventFilter:
    """Create a filter for a block height range."""
    return EventFilter(min_block_height=min_height, max_block_height=max_height)


def filter_by_time_range(min_time: int, max_time: int) -> EventFilter:
    """Create a filter for a timestamp range."""
    return EventFilter(min_timestamp=min_time, max_timestamp=max_time)


def filter_by_payload(key: str, value: Any) -> EventFilter:
    """Create a filter for a specific payload field value."""
    return EventFilter(payload_filters={key: value})
