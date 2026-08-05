"""
Unit tests for Event Snapshot.
"""

import pytest
from influx.events.event import Event, EventType, create_event
from influx.events.event_snapshot import EventSnapshot, EventSnapshotManager


class TestEventSnapshot:
    """Test EventSnapshot class."""

    def test_create_snapshot(self):
        """Test creating an event snapshot."""
        events = [
            create_event(EventType.SYSTEM_STARTUP, "system", {}, 0),
            create_event(EventType.BLOCK_FINALIZED, "consensus", {"block": 1}, 1),
        ]
        snapshot = EventSnapshot(
            snapshot_id="snap_001",
            block_height=1,
            events=events,
            root_hash=events[0].hash,
            tip_hash=events[-1].hash,
        )
        assert snapshot.snapshot_id == "snap_001"
        assert snapshot.block_height == 1
        assert len(snapshot.events) == 2
        assert snapshot.event_count == 2

    def test_snapshot_hash(self):
        """Test snapshot hash computation."""
        events = [create_event(EventType.SYSTEM_STARTUP, "system", {}, 0)]
        snapshot = EventSnapshot(
            snapshot_id="snap_001",
            block_height=0,
            events=events,
            root_hash=events[0].hash,
            tip_hash=events[0].hash,
        )
        h = snapshot.compute_hash()
        assert isinstance(h, str)
        assert len(h) == 64

    def test_snapshot_hash_determinism(self):
        """Test that same snapshot produces same hash."""
        events = [create_event(EventType.SYSTEM_STARTUP, "system", {}, 0)]
        snap1 = EventSnapshot(
            snapshot_id="snap_001",
            block_height=0,
            events=events,
            root_hash=events[0].hash,
            tip_hash=events[0].hash,
        )
        snap2 = EventSnapshot(
            snapshot_id="snap_001",
            block_height=0,
            events=events,
            root_hash=events[0].hash,
            tip_hash=events[0].hash,
        )
        assert snap1.hash == snap2.hash

    def test_verify_valid(self):
        """Test verification of valid snapshot."""
        events = [create_event(EventType.SYSTEM_STARTUP, "system", {}, 0)]
        snapshot = EventSnapshot(
            snapshot_id="snap_001",
            block_height=0,
            events=events,
            root_hash=events[0].hash,
            tip_hash=events[0].hash,
        )
        assert snapshot.verify() is True

    def test_verify_tampered(self):
        """Test verification of tampered snapshot."""
        events = [create_event(EventType.SYSTEM_STARTUP, "system", {}, 0)]
        snapshot = EventSnapshot(
            snapshot_id="snap_001",
            block_height=0,
            events=events,
            root_hash="wrong_hash",
            tip_hash=events[0].hash,
        )
        assert snapshot.verify() is False

    def test_snapshot_snapshot(self):
        """Test snapshot serialization."""
        events = [create_event(EventType.SYSTEM_STARTUP, "system", {}, 0)]
        snapshot = EventSnapshot(
            snapshot_id="snap_001",
            block_height=0,
            events=events,
            root_hash=events[0].hash,
            tip_hash=events[0].hash,
        )
        snap = snapshot.snapshot()
        assert snap["snapshot_id"] == "snap_001"
        assert snap["block_height"] == 0
        assert snap["event_count"] == 1


class TestEventSnapshotManager:
    """Test EventSnapshotManager class."""

    def test_create_snapshot(self):
        """Test creating a snapshot via manager."""
        manager = EventSnapshotManager()
        events = [
            create_event(EventType.SYSTEM_STARTUP, "system", {}, 0),
            create_event(EventType.BLOCK_FINALIZED, "consensus", {"block": 1}, 1),
        ]
        snapshot = manager.create_snapshot(
            events=events,
            block_height=1,
            root_hash=events[0].hash,
            tip_hash=events[-1].hash,
        )
        assert snapshot.block_height == 1
        assert snapshot.event_count == 2
        assert snapshot.snapshot_id is not None

    def test_get_snapshot(self):
        """Test retrieving a snapshot."""
        manager = EventSnapshotManager()
        events = [create_event(EventType.SYSTEM_STARTUP, "system", {}, 0)]
        created = manager.create_snapshot(events, 0, events[0].hash, events[0].hash)
        retrieved = manager.get_snapshot(created.snapshot_id)
        assert retrieved is not None
        assert retrieved.snapshot_id == created.snapshot_id

    def test_get_snapshot_not_found(self):
        """Test retrieving non-existent snapshot."""
        manager = EventSnapshotManager()
        assert manager.get_snapshot("nonexistent") is None

    def test_get_snapshot_by_block(self):
        """Test retrieving snapshot by block height."""
        manager = EventSnapshotManager()
        events = [create_event(EventType.SYSTEM_STARTUP, "system", {}, 0)]
        manager.create_snapshot(events, 0, events[0].hash, events[0].hash)
        events2 = [create_event(EventType.BLOCK_FINALIZED, "consensus", {}, 1)]
        manager.create_snapshot(events2, 1, events2[0].hash, events2[0].hash)
        snapshot = manager.get_snapshot_by_block(1)
        assert snapshot is not None
        assert snapshot.block_height == 1

    def test_get_snapshot_by_block_not_found(self):
        """Test retrieving snapshot by non-existent block."""
        manager = EventSnapshotManager()
        assert manager.get_snapshot_by_block(999) is None

    def test_get_latest_snapshot(self):
        """Test retrieving the latest snapshot."""
        manager = EventSnapshotManager()
        events1 = [create_event(EventType.SYSTEM_STARTUP, "system", {}, 0)]
        manager.create_snapshot(events1, 0, events1[0].hash, events1[0].hash)
        events2 = [create_event(EventType.BLOCK_FINALIZED, "consensus", {}, 1)]
        manager.create_snapshot(events2, 1, events2[0].hash, events2[0].hash)
        latest = manager.get_latest_snapshot()
        assert latest is not None
        assert latest.block_height == 1

    def test_get_latest_snapshot_empty(self):
        """Test latest snapshot on empty manager."""
        manager = EventSnapshotManager()
        assert manager.get_latest_snapshot() is None

    def test_snapshot_count(self):
        """Test snapshot count."""
        manager = EventSnapshotManager()
        assert manager.snapshot_count() == 0
        events = [create_event(EventType.SYSTEM_STARTUP, "system", {}, 0)]
        manager.create_snapshot(events, 0, events[0].hash, events[0].hash)
        assert manager.snapshot_count() == 1

    def test_get_all_snapshots(self):
        """Test getting all snapshots."""
        manager = EventSnapshotManager()
        events1 = [create_event(EventType.SYSTEM_STARTUP, "system", {}, 0)]
        manager.create_snapshot(events1, 0, events1[0].hash, events1[0].hash)
        events2 = [create_event(EventType.BLOCK_FINALIZED, "consensus", {}, 1)]
        manager.create_snapshot(events2, 1, events2[0].hash, events2[0].hash)
        all_snaps = manager.get_all_snapshots()
        assert len(all_snaps) == 2

    def test_verify_all_valid(self):
        """Test verifying all snapshots."""
        manager = EventSnapshotManager()
        events = [create_event(EventType.SYSTEM_STARTUP, "system", {}, 0)]
        manager.create_snapshot(events, 0, events[0].hash, events[0].hash)
        assert manager.verify_all() is True

    def test_snapshot(self):
        """Test manager snapshot."""
        manager = EventSnapshotManager()
        events = [create_event(EventType.SYSTEM_STARTUP, "system", {}, 0)]
        manager.create_snapshot(events, 0, events[0].hash, events[0].hash)
        snap = manager.snapshot()
        assert snap["snapshot_count"] == 1
        assert snap["latest_block_height"] == 0

    def test_reset(self):
        """Test resetting the manager."""
        manager = EventSnapshotManager()
        events = [create_event(EventType.SYSTEM_STARTUP, "system", {}, 0)]
        manager.create_snapshot(events, 0, events[0].hash, events[0].hash)
        assert manager.snapshot_count() == 1
        manager.reset()
        assert manager.snapshot_count() == 0
