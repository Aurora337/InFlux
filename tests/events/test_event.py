"""
Unit tests for the deterministic Event system.
"""

import pytest
from influx.events.event import Event, EventType, create_event


class TestEventCreation:
    """Test event creation and basic properties."""

    def test_create_event_minimal(self):
        """Test creating an event with minimal required fields."""
        event = create_event(
            event_type=EventType.SYSTEM_STARTUP,
            source="test",
            payload={"message": "hello"},
            block_height=1,
        )
        assert event.event_type == EventType.SYSTEM_STARTUP
        assert event.source == "test"
        assert event.payload == {"message": "hello"}
        assert event.block_height == 1
        assert event.sequence == 0
        assert event.previous_hash == ""
        assert event.event_id is not None
        assert len(event.event_id) == 32

    def test_create_event_with_all_fields(self):
        """Test creating an event with all optional fields."""
        event = create_event(
            event_type=EventType.PROPOSAL_CREATED,
            source="governance",
            payload={"proposal_id": "123", "title": "Test"},
            block_height=100,
            timestamp=1234567890,
            sequence=5,
            previous_hash="abc123",
        )
        assert event.event_type == EventType.PROPOSAL_CREATED
        assert event.source == "governance"
        assert event.block_height == 100
        assert event.timestamp == 1234567890
        assert event.sequence == 5
        assert event.previous_hash == "abc123"

    def test_event_hash_determinism(self):
        """Test that identical events produce identical hashes."""
        event1 = create_event(
            event_type=EventType.CONTRACT_DEPLOYED,
            source="runtime",
            payload={"contract_id": "ctr_001"},
            block_height=50,
            timestamp=1000,
        )
        event2 = create_event(
            event_type=EventType.CONTRACT_DEPLOYED,
            source="runtime",
            payload={"contract_id": "ctr_001"},
            block_height=50,
            timestamp=1000,
        )
        assert event1.hash == event2.hash

    def test_event_hash_different_payload(self):
        """Test that different payloads produce different hashes."""
        event1 = create_event(
            event_type=EventType.CONTRACT_DEPLOYED,
            source="runtime",
            payload={"contract_id": "ctr_001"},
            block_height=50,
        )
        event2 = create_event(
            event_type=EventType.CONTRACT_DEPLOYED,
            source="runtime",
            payload={"contract_id": "ctr_002"},
            block_height=50,
        )
        assert event1.hash != event2.hash

    def test_event_hash_different_type(self):
        """Test that different event types produce different hashes."""
        event1 = create_event(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            payload={},
            block_height=0,
        )
        event2 = create_event(
            event_type=EventType.SYSTEM_SHUTDOWN,
            source="system",
            payload={},
            block_height=0,
        )
        assert event1.hash != event2.hash


class TestEventVerification:
    """Test event hash verification."""

    def test_verify_valid_event(self):
        """Test that a valid event passes verification."""
        event = create_event(
            event_type=EventType.BALANCE_CHANGED,
            source="economics",
            payload={"account": "addr1", "delta": "100"},
            block_height=200,
        )
        assert event.verify() is True

    def test_verify_tampered_event(self):
        """Test that a tampered event fails verification."""
        event = create_event(
            event_type=EventType.BALANCE_CHANGED,
            source="economics",
            payload={"account": "addr1", "delta": "100"},
            block_height=200,
        )
        # Tamper with the payload
        event.payload["delta"] = "999"
        # The cached hash should no longer match
        assert event.verify() is False


class TestEventSnapshot:
    """Test event snapshot functionality."""

    def test_snapshot_contains_all_fields(self):
        """Test that snapshot contains all expected fields."""
        event = create_event(
            event_type=EventType.VALIDATOR_REWARDED,
            source="consensus",
            payload={"validator": "val_001", "amount": "500"},
            block_height=300,
            sequence=10,
            previous_hash="prev_hash",
        )
        snap = event.snapshot()
        assert snap["event_id"] == event.event_id
        assert snap["event_type"] == "validator_rewarded"
        assert snap["source"] == "consensus"
        assert snap["payload"]["validator"] == "val_001"
        assert snap["block_height"] == 300
        assert snap["sequence"] == 10
        assert snap["previous_hash"] == "prev_hash"
        assert snap["hash"] == event.hash

    def test_snapshot_hash_stability(self):
        """Test that snapshot hash remains stable for same input."""
        event = create_event(
            event_type=EventType.EPOCH_ADVANCED,
            source="system",
            payload={"epoch": 5},
            block_height=400,
            timestamp=5000,
        )
        snap1 = event.snapshot()
        snap2 = event.snapshot()
        assert snap1["hash"] == snap2["hash"]


class TestEventChainLinking:
    """Test event chain linking via previous_hash."""

    def test_chain_linking(self):
        """Test that events in a chain link correctly."""
        event1 = create_event(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            payload={},
            block_height=0,
            sequence=0,
        )
        event2 = create_event(
            event_type=EventType.BLOCK_FINALIZED,
            source="consensus",
            payload={"block": 1},
            block_height=1,
            sequence=1,
            previous_hash=event1.hash,
        )
        assert event2.previous_hash == event1.hash
        assert event2.verify() is True

    def test_chain_integrity_violation(self):
        """Test that broken chain linking is detected."""
        event1 = create_event(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            payload={},
            block_height=0,
        )
        event2 = create_event(
            event_type=EventType.BLOCK_FINALIZED,
            source="consensus",
            payload={"block": 1},
            block_height=1,
            previous_hash="wrong_hash",
        )
        assert event2.previous_hash != event1.hash


class TestEventTypeEnum:
    """Test EventType enum values."""

    def test_all_event_types_have_values(self):
        """Test that all event types have non-empty values."""
        for event_type in EventType:
            assert event_type.value is not None
            assert len(event_type.value) > 0

    def test_event_type_uniqueness(self):
        """Test that all event type values are unique."""
        values = [et.value for et in EventType]
        assert len(values) == len(set(values))

    def test_governance_event_types(self):
        """Test governance-specific event types."""
        assert EventType.PROPOSAL_CREATED.value == "proposal_created"
        assert EventType.PROPOSAL_APPROVED.value == "proposal_approved"
        assert EventType.PROPOSAL_EXECUTED.value == "proposal_executed"
        assert EventType.VOTE_CAST.value == "vote_cast"

    def test_economic_event_types(self):
        """Test economic-specific event types."""
        assert EventType.ECONOMIC_OPERATION.value == "economic_operation"
        assert EventType.BALANCE_CHANGED.value == "balance_changed"
        assert EventType.SUPPLY_CHANGED.value == "supply_changed"
        assert EventType.RESERVE_CHANGED.value == "reserve_changed"
