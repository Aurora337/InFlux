"""
Unit tests for the Event Queue.
"""

import pytest
from influx.events.event import Event, EventType, create_event
from influx.events.event_queue import EventQueue


class TestEventQueue:
    """Test EventQueue class."""

    def test_push_event(self):
        """Test pushing an event onto the queue."""
        queue = EventQueue()
        event = queue.push(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            payload={"msg": "hello"},
            block_height=0,
        )
        assert queue.event_count() == 1
        assert event.sequence == 0
        assert event.previous_hash == ""

    def test_push_multiple_events(self):
        """Test pushing multiple events."""
        queue = EventQueue()
        e1 = queue.push(EventType.SYSTEM_STARTUP, "system", {}, 0)
        e2 = queue.push(EventType.BLOCK_FINALIZED, "consensus", {"block": 1}, 1)
        e3 = queue.push(EventType.BLOCK_FINALIZED, "consensus", {"block": 2}, 2)
        assert queue.event_count() == 3
        assert e1.sequence == 0
        assert e2.sequence == 1
        assert e3.sequence == 2
        assert e2.previous_hash == e1.hash
        assert e3.previous_hash == e2.hash

    def test_push_event_external(self):
        """Test pushing an externally created event."""
        queue = EventQueue()
        event = create_event(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            payload={},
            block_height=0,
            sequence=0,
        )
        result = queue.push_event(event)
        assert result is True
        assert queue.event_count() == 1

    def test_push_event_external_wrong_sequence(self):
        """Test that wrong sequence number is rejected."""
        queue = EventQueue()
        event = create_event(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            payload={},
            block_height=0,
            sequence=5,  # Wrong sequence
        )
        result = queue.push_event(event)
        assert result is False
        assert queue.event_count() == 0

    def test_replay(self):
        """Test replaying events."""
        queue = EventQueue()
        queue.push(EventType.SYSTEM_STARTUP, "system", {}, 0)
        queue.push(EventType.BLOCK_FINALIZED, "consensus", {"block": 1}, 1)
        events = queue.replay()
        assert len(events) == 2
        assert events[0].event_type == EventType.SYSTEM_STARTUP
        assert events[1].event_type == EventType.BLOCK_FINALIZED

    def test_replay_range(self):
        """Test replaying a range of events."""
        queue = EventQueue()
        queue.push(EventType.SYSTEM_STARTUP, "system", {}, 0)
        queue.push(EventType.BLOCK_FINALIZED, "consensus", {"block": 1}, 1)
        queue.push(EventType.BLOCK_FINALIZED, "consensus", {"block": 2}, 2)
        events = queue.replay(start_index=1, end_index=3)
        assert len(events) == 2
        assert events[0].block_height == 1
        assert events[1].block_height == 2

    def test_replay_by_block(self):
        """Test replaying events by block height."""
        queue = EventQueue()
        queue.push(EventType.SYSTEM_STARTUP, "system", {}, 0)
        queue.push(EventType.BLOCK_FINALIZED, "consensus", {"block": 1}, 1)
        queue.push(EventType.BALANCE_CHANGED, "economics", {}, 1)
        events = queue.replay_by_block(1)
        assert len(events) == 2
        assert all(e.block_height == 1 for e in events)

    def test_get_event(self):
        """Test getting a specific event by ID."""
        queue = EventQueue()
        event = queue.push(EventType.SYSTEM_STARTUP, "system", {}, 0)
        retrieved = queue.get_event(event.event_id)
        assert retrieved is not None
        assert retrieved.event_id == event.event_id

    def test_get_event_not_found(self):
        """Test getting a non-existent event."""
        queue = EventQueue()
        retrieved = queue.get_event("nonexistent")
        assert retrieved is None

    def test_get_events_by_type(self):
        """Test getting events by type."""
        queue = EventQueue()
        queue.push(EventType.SYSTEM_STARTUP, "system", {}, 0)
        queue.push(EventType.BLOCK_FINALIZED, "consensus", {}, 1)
        queue.push(EventType.BLOCK_FINALIZED, "consensus", {}, 2)
        events = queue.get_events_by_type(EventType.BLOCK_FINALIZED)
        assert len(events) == 2

    def test_get_events_by_source(self):
        """Test getting events by source."""
        queue = EventQueue()
        queue.push(EventType.SYSTEM_STARTUP, "system", {}, 0)
        queue.push(EventType.SYSTEM_SHUTDOWN, "system", {}, 1)
        queue.push(EventType.BLOCK_FINALIZED, "consensus", {}, 2)
        events = queue.get_events_by_source("system")
        assert len(events) == 2

    def test_get_block_heights(self):
        """Test getting all block heights."""
        queue = EventQueue()
        queue.push(EventType.SYSTEM_STARTUP, "system", {}, 0)
        queue.push(EventType.BLOCK_FINALIZED, "consensus", {}, 5)
        queue.push(EventType.BLOCK_FINALIZED, "consensus", {}, 10)
        heights = queue.get_block_heights()
        assert heights == [0, 5, 10]

    def test_verify_integrity_valid(self):
        """Test integrity verification of valid chain."""
        queue = EventQueue()
        queue.push(EventType.SYSTEM_STARTUP, "system", {}, 0)
        queue.push(EventType.BLOCK_FINALIZED, "consensus", {}, 1)
        assert queue.verify_integrity() is True

    def test_verify_integrity_empty(self):
        """Test integrity verification of empty queue."""
        queue = EventQueue()
        assert queue.verify_integrity() is True

    def test_compute_root_hash(self):
        """Test root hash computation."""
        queue = EventQueue()
        assert queue.compute_root_hash() == ""
        event = queue.push(EventType.SYSTEM_STARTUP, "system", {}, 0)
        assert queue.compute_root_hash() == event.hash

    def test_compute_tip_hash(self):
        """Test tip hash computation."""
        queue = EventQueue()
        assert queue.compute_tip_hash() == ""
        queue.push(EventType.SYSTEM_STARTUP, "system", {}, 0)
        event = queue.push(EventType.BLOCK_FINALIZED, "consensus", {}, 1)
        assert queue.compute_tip_hash() == event.hash

    def test_compute_block_hash(self):
        """Test block hash computation."""
        queue = EventQueue()
        queue.push(EventType.SYSTEM_STARTUP, "system", {}, 0)
        queue.push(EventType.BLOCK_FINALIZED, "consensus", {}, 1)
        queue.push(EventType.BALANCE_CHANGED, "economics", {}, 1)
        block_hash = queue.compute_block_hash(1)
        assert isinstance(block_hash, str)
        assert len(block_hash) == 64

    def test_compute_block_hash_empty(self):
        """Test block hash for non-existent block."""
        queue = EventQueue()
        assert queue.compute_block_hash(999) == ""

    def test_snapshot(self):
        """Test queue snapshot."""
        queue = EventQueue()
        queue.push(EventType.SYSTEM_STARTUP, "system", {}, 0)
        snap = queue.snapshot()
        assert snap["event_count"] == 1
        assert snap["root_hash"] == queue.compute_root_hash()
        assert snap["tip_hash"] == queue.compute_tip_hash()

    def test_reset(self):
        """Test resetting the queue."""
        queue = EventQueue()
        queue.push(EventType.SYSTEM_STARTUP, "system", {}, 0)
        assert queue.event_count() == 1
        queue.reset()
        assert queue.event_count() == 0
        assert queue.compute_root_hash() == ""
