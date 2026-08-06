"""
Unit tests for the Event Filter.
"""

import pytest
from influx.events.event import EventType, create_event
from influx.events.event_filter import (
    EventFilter,
    filter_by_type,
    filter_by_source,
    filter_by_block_range,
    filter_by_time_range,
    filter_by_payload,
)


@pytest.fixture
def sample_events():
    """Create sample events for testing."""
    return [
        create_event(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            payload={"version": "1.0"},
            block_height=0,
            timestamp=1000,
        ),
        create_event(
            event_type=EventType.BLOCK_FINALIZED,
            source="consensus",
            payload={"block": 1},
            block_height=1,
            timestamp=2000,
        ),
        create_event(
            event_type=EventType.BALANCE_CHANGED,
            source="economics",
            payload={"account": "addr1", "delta": "100"},
            block_height=2,
            timestamp=3000,
        ),
        create_event(
            event_type=EventType.BLOCK_FINALIZED,
            source="consensus",
            payload={"block": 2},
            block_height=2,
            timestamp=3000,
        ),
    ]


class TestEventFilter:
    """Test EventFilter class."""

    def test_filter_by_type(self, sample_events):
        """Test filtering by event type."""
        f = EventFilter(event_types={EventType.BLOCK_FINALIZED})
        results = f.apply(sample_events)
        assert len(results) == 2
        assert all(e.event_type == EventType.BLOCK_FINALIZED for e in results)

    def test_filter_by_source(self, sample_events):
        """Test filtering by source."""
        f = EventFilter(sources={"consensus"})
        results = f.apply(sample_events)
        assert len(results) == 2
        assert all(e.source == "consensus" for e in results)

    def test_filter_by_block_range(self, sample_events):
        """Test filtering by block height range."""
        f = EventFilter(min_block_height=1, max_block_height=2)
        results = f.apply(sample_events)
        assert len(results) == 3
        assert all(1 <= e.block_height <= 2 for e in results)

    def test_filter_by_time_range(self, sample_events):
        """Test filtering by timestamp range."""
        f = EventFilter(min_timestamp=2000, max_timestamp=3000)
        results = f.apply(sample_events)
        assert len(results) == 3

    def test_filter_by_payload(self, sample_events):
        """Test filtering by payload field."""
        f = EventFilter(payload_filters={"block": 1})
        results = f.apply(sample_events)
        assert len(results) == 1
        assert results[0].payload["block"] == 1

    def test_filter_multiple_criteria(self, sample_events):
        """Test filtering with multiple criteria."""
        f = EventFilter(
            event_types={EventType.BLOCK_FINALIZED},
            sources={"consensus"},
            min_block_height=1,
        )
        results = f.apply(sample_events)
        assert len(results) == 2

    def test_filter_no_match(self, sample_events):
        """Test filter with no matches."""
        f = EventFilter(event_types={EventType.PROPOSAL_CREATED})
        results = f.apply(sample_events)
        assert len(results) == 0

    def test_filter_all_match(self, sample_events):
        """Test filter that matches all events."""
        f = EventFilter()
        results = f.apply(sample_events)
        assert len(results) == 4

    def test_custom_predicate(self, sample_events):
        """Test custom predicate filter."""
        f = EventFilter(
            custom_predicates=[lambda e: e.block_height > 0]
        )
        results = f.apply(sample_events)
        assert len(results) == 3

    def test_and_filter(self, sample_events):
        """Test AND combination of filters."""
        f1 = EventFilter(event_types={EventType.BLOCK_FINALIZED})
        f2 = EventFilter(sources={"consensus"})
        combined = f1.and_filter(f2)
        results = combined.apply(sample_events)
        assert len(results) == 2

    def test_or_filter(self, sample_events):
        """Test OR combination of filters."""
        f1 = EventFilter(event_types={EventType.SYSTEM_STARTUP})
        f2 = EventFilter(event_types={EventType.BALANCE_CHANGED})
        combined = f1.or_filter(f2)
        results = combined.apply(sample_events)
        assert len(results) == 2

    def test_negate_filter(self, sample_events):
        """Test negated filter."""
        f = EventFilter(event_types={EventType.BLOCK_FINALIZED})
        negated = f.negate()
        results = negated.apply(sample_events)
        assert len(results) == 2
        assert all(e.event_type != EventType.BLOCK_FINALIZED for e in results)

    def test_snapshot(self):
        """Test filter snapshot."""
        f = EventFilter(
            event_types={EventType.SYSTEM_STARTUP},
            sources={"system"},
            min_block_height=0,
        )
        snap = f.snapshot()
        assert "system_startup" in snap["event_types"]
        assert "system" in snap["sources"]
        assert snap["min_block_height"] == 0


class TestFilterHelpers:
    """Test filter helper functions."""

    def test_filter_by_type_helper(self):
        """Test filter_by_type helper."""
        f = filter_by_type(EventType.SYSTEM_STARTUP)
        assert f.event_types == {EventType.SYSTEM_STARTUP}

    def test_filter_by_source_helper(self):
        """Test filter_by_source helper."""
        f = filter_by_source("system")
        assert f.sources == {"system"}

    def test_filter_by_block_range_helper(self):
        """Test filter_by_block_range helper."""
        f = filter_by_block_range(10, 20)
        assert f.min_block_height == 10
        assert f.max_block_height == 20

    def test_filter_by_time_range_helper(self):
        """Test filter_by_time_range helper."""
        f = filter_by_time_range(1000, 2000)
        assert f.min_timestamp == 1000
        assert f.max_timestamp == 2000

    def test_filter_by_payload_helper(self):
        """Test filter_by_payload helper."""
        f = filter_by_payload("key", "value")
        assert f.payload_filters == {"key": "value"}
