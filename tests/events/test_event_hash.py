"""
Unit tests for event content hashing utilities.
"""

import pytest
from influx.events.event import Event, EventType, create_event
from influx.events.event_hash import (
    compute_content_hash,
    verify_event_chain,
    verify_event_chain_from_root,
    compute_chain_root,
    compute_chain_tip,
    hash_event_type,
    hash_event_fields,
)


class TestContentHash:
    """Test content hash computation."""

    def test_compute_content_hash_deterministic(self):
        """Test that same payload produces same hash."""
        payload = {"key": "value", "number": 42}
        hash1 = compute_content_hash(payload)
        hash2 = compute_content_hash(payload)
        assert hash1 == hash2

    def test_compute_content_hash_different(self):
        """Test that different payloads produce different hashes."""
        hash1 = compute_content_hash({"a": 1})
        hash2 = compute_content_hash({"a": 2})
        assert hash1 != hash2

    def test_compute_content_hash_sorted_keys(self):
        """Test that keys are sorted for deterministic output."""
        hash1 = compute_content_hash({"b": 2, "a": 1})
        hash2 = compute_content_hash({"a": 1, "b": 2})
        assert hash1 == hash2

    def test_compute_content_hash_nested(self):
        """Test hashing of nested dictionaries."""
        payload = {"outer": {"inner": "value", "num": 10}}
        hash1 = compute_content_hash(payload)
        hash2 = compute_content_hash(payload)
        assert hash1 == hash2

    def test_compute_content_hash_empty(self):
        """Test hashing of empty dictionary."""
        h = compute_content_hash({})
        assert isinstance(h, str)
        assert len(h) == 64  # SHA-256 hex


class TestEventChain:
    """Test event chain verification."""

    def test_verify_empty_chain(self):
        """Test that empty chain is valid."""
        assert verify_event_chain([]) is True

    def test_verify_single_event(self):
        """Test that single event chain is valid."""
        event = create_event(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            payload={},
            block_height=0,
        )
        assert verify_event_chain([event]) is True

    def test_verify_valid_chain(self):
        """Test that a properly linked chain is valid."""
        e1 = create_event(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            payload={},
            block_height=0,
            sequence=0,
        )
        e2 = create_event(
            event_type=EventType.BLOCK_FINALIZED,
            source="consensus",
            payload={"block": 1},
            block_height=1,
            sequence=1,
            previous_hash=e1.hash,
        )
        e3 = create_event(
            event_type=EventType.BLOCK_FINALIZED,
            source="consensus",
            payload={"block": 2},
            block_height=2,
            sequence=2,
            previous_hash=e2.hash,
        )
        assert verify_event_chain([e1, e2, e3]) is True

    def test_verify_broken_chain(self):
        """Test that a broken chain is detected."""
        e1 = create_event(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            payload={},
            block_height=0,
        )
        e2 = create_event(
            event_type=EventType.BLOCK_FINALIZED,
            source="consensus",
            payload={"block": 1},
            block_height=1,
            previous_hash="wrong_hash",
        )
        assert verify_event_chain([e1, e2]) is False

    def test_verify_chain_from_root(self):
        """Test chain verification from root hash."""
        e1 = create_event(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            payload={},
            block_height=0,
        )
        e2 = create_event(
            event_type=EventType.BLOCK_FINALIZED,
            source="consensus",
            payload={"block": 1},
            block_height=1,
            previous_hash=e1.hash,
        )
        assert verify_event_chain_from_root([e1, e2], e1.hash) is True
        assert verify_event_chain_from_root([e1, e2], "wrong_root") is False


class TestChainRootAndTip:
    """Test chain root and tip computation."""

    def test_empty_chain_root(self):
        """Test root of empty chain."""
        assert compute_chain_root([]) == ""

    def test_empty_chain_tip(self):
        """Test tip of empty chain."""
        assert compute_chain_tip([]) == ""

    def test_chain_root(self):
        """Test root hash computation."""
        e1 = create_event(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            payload={},
            block_height=0,
        )
        e2 = create_event(
            event_type=EventType.BLOCK_FINALIZED,
            source="consensus",
            payload={"block": 1},
            block_height=1,
            previous_hash=e1.hash,
        )
        assert compute_chain_root([e1, e2]) == e1.hash

    def test_chain_tip(self):
        """Test tip hash computation."""
        e1 = create_event(
            event_type=EventType.SYSTEM_STARTUP,
            source="system",
            payload={},
            block_height=0,
        )
        e2 = create_event(
            event_type=EventType.BLOCK_FINALIZED,
            source="consensus",
            payload={"block": 1},
            block_height=1,
            previous_hash=e1.hash,
        )
        assert compute_chain_tip([e1, e2]) == e2.hash


class TestHashUtilities:
    """Test hash utility functions."""

    def test_hash_event_type(self):
        """Test event type hashing."""
        h = hash_event_type(EventType.SYSTEM_STARTUP)
        assert isinstance(h, str)
        assert len(h) == 64

    def test_hash_event_type_deterministic(self):
        """Test that same type produces same hash."""
        h1 = hash_event_type(EventType.SYSTEM_STARTUP)
        h2 = hash_event_type(EventType.SYSTEM_STARTUP)
        assert h1 == h2

    def test_hash_event_fields(self):
        """Test event field hashing."""
        fields = {"key": "value", "num": 42}
        h = hash_event_fields(fields)
        assert isinstance(h, str)
        assert len(h) == 64

    def test_hash_event_fields_deterministic(self):
        """Test that same fields produce same hash."""
        h1 = hash_event_fields({"a": 1, "b": 2})
        h2 = hash_event_fields({"b": 2, "a": 1})
        assert h1 == h2
