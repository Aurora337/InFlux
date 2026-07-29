"""
Unit tests for the governance proposal module.

Tests proposal creation, lifecycle transitions, hashing determinism,
serialization, validation, and snapshot behavior.
"""

import hashlib
import json
from datetime import datetime, timezone

import pytest

from influx.governance.proposal import (
    Proposal,
    ProposalStatus,
    ProposalType,
    ProposalLifecycle,
)


class TestProposalCreation:
    """Proposal creation and initialization tests."""

    def test_create_text_proposal(self):
        """Create a TEXT type proposal with all required fields."""
        proposal = Proposal(
            proposal_id="prop-001",
            title="Test Proposal",
            description="A test governance proposal",
            proposer="alice",
            proposal_type=ProposalType.TEXT,
        )
        assert proposal.proposal_id == "prop-001"
        assert proposal.title == "Test Proposal"
        assert proposal.description == "A test governance proposal"
        assert proposal.proposer == "alice"
        assert proposal.proposal_type == ProposalType.TEXT
        assert proposal.lifecycle.current == ProposalStatus.DRAFT

    def test_create_all_proposal_types(self):
        """Create proposals of each type and verify defaults."""
        types = [
            ProposalType.TEXT,
            ProposalType.PARAMETER_CHANGE,
            ProposalType.UPGRADE,
            ProposalType.TREASURY,
            ProposalType.ECONOMIC,
        ]
        for pt in types:
            proposal = Proposal(
                proposal_id=f"prop-{pt.value}",
                title=f"{pt.value} proposal",
                description=f"A {pt.value} type proposal",
                proposer="bob",
                proposal_type=pt,
            )
            assert proposal.proposal_type == pt
            assert proposal.quorum == 0.4
            assert proposal.approval_threshold == 0.5
            assert proposal.execution_delay_blocks == 100
            assert proposal.target_block_height == 0
            assert proposal.metadata == {}
            assert proposal._hash is None

    def test_proposal_with_custom_parameters(self):
        """Create proposal with custom quorum, threshold, and metadata."""
        proposal = Proposal(
            proposal_id="prop-custom",
            title="Custom Proposal",
            description="With custom settings",
            proposer="carol",
            proposal_type=ProposalType.PARAMETER_CHANGE,
            quorum=0.6,
            approval_threshold=0.66,
            execution_delay_blocks=200,
            target_block_height=5000,
            metadata={"key": "value", "param": "new_value"},
        )
        assert proposal.quorum == 0.6
        assert proposal.approval_threshold == 0.66
        assert proposal.execution_delay_blocks == 200
        assert proposal.target_block_height == 5000
        assert proposal.metadata == {"key": "value", "param": "new_value"}


class TestProposalValidation:
    """Proposal validation tests."""

    def test_valid_proposal(self):
        """A properly constructed proposal should validate."""
        proposal = Proposal(
            proposal_id="prop-valid",
            title="Valid Proposal",
            description="A valid proposal",
            proposer="alice",
            proposal_type=ProposalType.TEXT,
        )
        assert proposal.validate() is True

    def test_empty_proposal_id_rejected(self):
        """Empty proposal_id should fail validation."""
        proposal = Proposal(
            proposal_id="",
            title="No ID",
            description="Missing proposal ID",
            proposer="alice",
            proposal_type=ProposalType.TEXT,
        )
        assert proposal.validate() is False

    def test_empty_title_rejected(self):
        """Empty title should fail validation."""
        proposal = Proposal(
            proposal_id="prop-002",
            title="",
            description="Missing title",
            proposer="alice",
            proposal_type=ProposalType.TEXT,
        )
        assert proposal.validate() is False

    def test_empty_proposer_rejected(self):
        """Empty proposer should fail validation."""
        proposal = Proposal(
            proposal_id="prop-003",
            title="A Proposal",
            description="Missing proposer",
            proposer="",
            proposal_type=ProposalType.TEXT,
        )
        assert proposal.validate() is False

    def test_invalid_quorum_low(self):
        """Quorum below 0 should fail validation."""
        proposal = Proposal(
            proposal_id="prop-004",
            title="Invalid Quorum",
            description="Quorum is negative",
            proposer="alice",
            proposal_type=ProposalType.TEXT,
            quorum=-0.1,
        )
        assert proposal.validate() is False

    def test_invalid_quorum_high(self):
        """Quorum above 1 should fail validation."""
        proposal = Proposal(
            proposal_id="prop-005",
            title="Invalid Quorum High",
            description="Quorum above 1",
            proposer="alice",
            proposal_type=ProposalType.TEXT,
            quorum=1.5,
        )
        assert proposal.validate() is False

    def test_invalid_approval_threshold_low(self):
        """Approval threshold below 0 should fail validation."""
        proposal = Proposal(
            proposal_id="prop-006",
            title="Invalid Threshold",
            description="Threshold negative",
            proposer="alice",
            proposal_type=ProposalType.TEXT,
            approval_threshold=-0.5,
        )
        assert proposal.validate() is False

    def test_invalid_approval_threshold_high(self):
        """Approval threshold above 1 should fail validation."""
        proposal = Proposal(
            proposal_id="prop-007",
            title="Invalid Threshold High",
            description="Threshold above 1",
            proposer="alice",
            proposal_type=ProposalType.TEXT,
            approval_threshold=1.5,
        )
        assert proposal.validate() is False

    def test_negative_execution_delay(self):
        """Negative execution delay should fail validation."""
        proposal = Proposal(
            proposal_id="prop-008",
            title="Negative Delay",
            description="Execution delay negative",
            proposer="alice",
            proposal_type=ProposalType.TEXT,
            execution_delay_blocks=-1,
        )
        assert proposal.validate() is False

    def test_hash_integrity_check(self):
        """Proposal with corrupted hash should fail validation."""
        proposal = Proposal(
            proposal_id="prop-009",
            title="Hash Integrity",
            description="Testing hash validation",
            proposer="alice",
            proposal_type=ProposalType.TEXT,
        )
        # Force hash to a different value
        proposal._hash = "invalid_hash"
        assert proposal.validate() is False


class TestProposalHashDeterminism:
    """Proposal hash determinism tests."""

    def test_same_proposal_same_hash(self):
        """Same proposal fields always produce the same hash."""
        p1 = Proposal(
            proposal_id="prop-hash-1",
            title="Hash Test",
            description="Testing hash determinism",
            proposer="alice",
            proposal_type=ProposalType.TEXT,
        )
        p2 = Proposal(
            proposal_id="prop-hash-1",
            title="Hash Test",
            description="Testing hash determinism",
            proposer="alice",
            proposal_type=ProposalType.TEXT,
        )
        assert p1.hash == p2.hash

    def test_different_proposals_different_hashes(self):
        """Different proposals should produce different hashes."""
        p1 = Proposal(
            proposal_id="prop-a",
            title="Proposal A",
            description="First proposal",
            proposer="alice",
            proposal_type=ProposalType.TEXT,
        )
        p2 = Proposal(
            proposal_id="prop-b",
            title="Proposal B",
            description="Second proposal",
            proposer="bob",
            proposal_type=ProposalType.UPGRADE,
        )
        assert p1.hash != p2.hash

    def test_hash_is_sha256(self):
        """Hash should be a valid SHA-256 hex digest."""
        proposal = Proposal(
            proposal_id="prop-sha256",
            title="SHA256 Check",
            description="Verify hash format",
            proposer="alice",
            proposal_type=ProposalType.TEXT,
        )
        assert len(proposal.hash) == 64
        # Verify it's valid hex
        int(proposal.hash, 16)

    def test_hash_cache(self):
        """Hash should be cached after first computation."""
        proposal = Proposal(
            proposal_id="prop-cache",
            title="Cache Test",
            description="Test hash caching",
            proposer="alice",
            proposal_type=ProposalType.TEXT,
        )
        first_hash = proposal.hash
        # Access again - should return cached value
        second_hash = proposal.hash
        assert first_hash == second_hash
        assert proposal._hash is not None

    def test_compute_hash_matches_property(self):
        """compute_hash() should return same value as hash property."""
        proposal = Proposal(
            proposal_id="prop-compare",
            title="Compare Test",
            description="Test compute_hash vs property",
            proposer="alice",
            proposal_type=ProposalType.TEXT,
        )
        # Clear cache then compute
        proposal._hash = None
        computed = proposal.compute_hash()
        # Property should also compute
        cached = proposal.hash
        assert computed == cached


class TestProposalSerializationDeterminism:
    """Proposal serialization determinism tests."""

    def test_canonical_serialization_consistent(self):
        """Canonical JSON serialization should be consistent."""
        proposal = Proposal(
            proposal_id="prop-serial",
            title="Serialization Test",
            description="Testing canonical serialization",
            proposer="alice",
            proposal_type=ProposalType.TEXT,
            metadata={"z_key": "last", "a_key": "first"},
        )
        # Compute hash twice - should be identical
        hash1 = proposal.compute_hash()
        hash2 = proposal.compute_hash()
        assert hash1 == hash2

    def test_metadata_order_invariant(self):
        """Hash should be invariant to metadata insertion order."""
        p1 = Proposal(
            proposal_id="prop-meta",
            title="Meta Test",
            description="Testing metadata order",
            proposer="alice",
            proposal_type=ProposalType.TEXT,
            metadata={"a": 1, "b": 2, "c": 3},
        )
        p2 = Proposal(
            proposal_id="prop-meta",
            title="Meta Test",
            description="Testing metadata order",
            proposer="alice",
            proposal_type=ProposalType.TEXT,
            metadata={"c": 3, "b": 2, "a": 1},
        )
        assert p1.hash == p2.hash

    def test_snapshot_includes_all_fields(self):
        """Snapshot should include all expected fields."""
        proposal = Proposal(
            proposal_id="prop-snap",
            title="Snapshot Test",
            description="Testing snapshot output",
            proposer="alice",
            proposal_type=ProposalType.TEXT,
            target_block_height=1000,
            quorum=0.5,
            approval_threshold=0.6,
        )
        snapshot = proposal.snapshot()
        assert snapshot["proposal_id"] == "prop-snap"
        assert snapshot["title"] == "Snapshot Test"
        assert snapshot["proposer"] == "alice"
        assert snapshot["proposal_type"] == "text"
        assert snapshot["status"] == "draft"
        assert snapshot["hash"] == proposal.hash
        assert snapshot["lifecycle"]["current"] == "draft"
        assert snapshot["target_block_height"] == 1000
        assert snapshot["quorum"] == 0.5
        assert snapshot["approval_threshold"] == 0.6


class TestProposalLifecycle:
    """Proposal lifecycle state machine tests."""

    def test_full_valid_path(self):
        """Test complete valid lifecycle: DRAFT→PENDING→ACTIVE→PASSED→EXECUTED."""
        lifecycle = ProposalLifecycle()
        assert lifecycle.current == ProposalStatus.DRAFT

        assert lifecycle.transition(ProposalStatus.PENDING) is True
        assert lifecycle.current == ProposalStatus.PENDING

        assert lifecycle.transition(ProposalStatus.ACTIVE) is True
        assert lifecycle.current == ProposalStatus.ACTIVE
        assert lifecycle.activated_at is not None

        assert lifecycle.transition(ProposalStatus.PASSED) is True
        assert lifecycle.current == ProposalStatus.PASSED
        assert lifecycle.resolved_at is not None

        assert lifecycle.transition(ProposalStatus.EXECUTED) is True
        assert lifecycle.current == ProposalStatus.EXECUTED
        assert lifecycle.executed_at is not None

    def test_draft_to_pending(self):
        """DRAFT should transition to PENDING."""
        lifecycle = ProposalLifecycle()
        assert lifecycle.transition(ProposalStatus.PENDING) is True
        assert lifecycle.current == ProposalStatus.PENDING

    def test_draft_to_expired(self):
        """DRAFT should transition to EXPIRED."""
        lifecycle = ProposalLifecycle()
        assert lifecycle.transition(ProposalStatus.EXPIRED) is True
        assert lifecycle.current == ProposalStatus.EXPIRED

    def test_pending_to_active(self):
        """PENDING should transition to ACTIVE."""
        lifecycle = ProposalLifecycle()
        lifecycle.transition(ProposalStatus.PENDING)
        assert lifecycle.transition(ProposalStatus.ACTIVE) is True
        assert lifecycle.current == ProposalStatus.ACTIVE

    def test_pending_to_vetoed(self):
        """PENDING should transition to VETOED."""
        lifecycle = ProposalLifecycle()
        lifecycle.transition(ProposalStatus.PENDING)
        assert lifecycle.transition(ProposalStatus.VETOED) is True
        assert lifecycle.current == ProposalStatus.VETOED

    def test_active_to_passed(self):
        """ACTIVE should transition to PASSED."""
        lifecycle = ProposalLifecycle()
        lifecycle.transition(ProposalStatus.PENDING)
        lifecycle.transition(ProposalStatus.ACTIVE)
        assert lifecycle.transition(ProposalStatus.PASSED) is True
        assert lifecycle.current == ProposalStatus.PASSED

    def test_active_to_failed(self):
        """ACTIVE should transition to FAILED."""
        lifecycle = ProposalLifecycle()
        lifecycle.transition(ProposalStatus.PENDING)
        lifecycle.transition(ProposalStatus.ACTIVE)
        assert lifecycle.transition(ProposalStatus.FAILED) is True
        assert lifecycle.current == ProposalStatus.FAILED

    def test_active_to_vetoed(self):
        """ACTIVE should transition to VETOED."""
        lifecycle = ProposalLifecycle()
        lifecycle.transition(ProposalStatus.PENDING)
        lifecycle.transition(ProposalStatus.ACTIVE)
        assert lifecycle.transition(ProposalStatus.VETOED) is True
        assert lifecycle.current == ProposalStatus.VETOED

    def test_active_to_expired(self):
        """ACTIVE should transition to EXPIRED."""
        lifecycle = ProposalLifecycle()
        lifecycle.transition(ProposalStatus.PENDING)
        lifecycle.transition(ProposalStatus.ACTIVE)
        assert lifecycle.transition(ProposalStatus.EXPIRED) is True
        assert lifecycle.current == ProposalStatus.EXPIRED

    def test_passed_to_executed(self):
        """PASSED should transition to EXECUTED."""
        lifecycle = ProposalLifecycle()
        lifecycle.transition(ProposalStatus.PENDING)
        lifecycle.transition(ProposalStatus.ACTIVE)
        lifecycle.transition(ProposalStatus.PASSED)
        assert lifecycle.transition(ProposalStatus.EXECUTED) is True
        assert lifecycle.current == ProposalStatus.EXECUTED

    def test_failed_terminal_state(self):
        """FAILED should be a terminal state."""
        lifecycle = ProposalLifecycle()
        lifecycle.transition(ProposalStatus.PENDING)
        lifecycle.transition(ProposalStatus.ACTIVE)
        lifecycle.transition(ProposalStatus.FAILED)
        # No valid transitions from FAILED
        assert lifecycle.transition(ProposalStatus.EXECUTED) is False
        assert lifecycle.transition(ProposalStatus.PASSED) is False
        assert lifecycle.transition(ProposalStatus.ACTIVE) is False
        assert lifecycle.current == ProposalStatus.FAILED

    def test_executed_terminal_state(self):
        """EXECUTED should be a terminal state."""
        lifecycle = ProposalLifecycle()
        lifecycle.transition(ProposalStatus.PENDING)
        lifecycle.transition(ProposalStatus.ACTIVE)
        lifecycle.transition(ProposalStatus.PASSED)
        lifecycle.transition(ProposalStatus.EXECUTED)
        # No valid transitions from EXECUTED
        assert lifecycle.transition(ProposalStatus.PASSED) is False
        assert lifecycle.transition(ProposalStatus.ACTIVE) is False
        assert lifecycle.current == ProposalStatus.EXECUTED

    def test_expired_terminal_state(self):
        """EXPIRED should be a terminal state."""
        lifecycle = ProposalLifecycle()
        lifecycle.transition(ProposalStatus.PENDING)
        lifecycle.transition(ProposalStatus.EXPIRED)
        assert lifecycle.transition(ProposalStatus.ACTIVE) is False
        assert lifecycle.current == ProposalStatus.EXPIRED

    def test_vetoed_terminal_state(self):
        """VETOED should be a terminal state."""
        lifecycle = ProposalLifecycle()
        lifecycle.transition(ProposalStatus.PENDING)
        lifecycle.transition(ProposalStatus.VETOED)
        assert lifecycle.transition(ProposalStatus.ACTIVE) is False
        assert lifecycle.current == ProposalStatus.VETOED

    def test_invalid_transition_draft_to_executed(self):
        """DRAFT should not transition directly to EXECUTED."""
        lifecycle = ProposalLifecycle()
        assert lifecycle.transition(ProposalStatus.EXECUTED) is False
        assert lifecycle.current == ProposalStatus.DRAFT

    def test_invalid_transition_draft_to_passed(self):
        """DRAFT should not transition directly to PASSED."""
        lifecycle = ProposalLifecycle()
        assert lifecycle.transition(ProposalStatus.PASSED) is False
        assert lifecycle.current == ProposalStatus.DRAFT

    def test_invalid_transition_draft_to_failed(self):
        """DRAFT should not transition directly to FAILED."""
        lifecycle = ProposalLifecycle()
        assert lifecycle.transition(ProposalStatus.FAILED) is False
        assert lifecycle.current == ProposalStatus.DRAFT

    def test_invalid_transition_draft_to_vetoed(self):
        """DRAFT should not transition directly to VETOED."""
        lifecycle = ProposalLifecycle()
        assert lifecycle.transition(ProposalStatus.VETOED) is False
        assert lifecycle.current == ProposalStatus.DRAFT

    def test_invalid_transition_passed_to_active(self):
        """PASSED should not transition back to ACTIVE."""
        lifecycle = ProposalLifecycle()
        lifecycle.transition(ProposalStatus.PENDING)
        lifecycle.transition(ProposalStatus.ACTIVE)
        lifecycle.transition(ProposalStatus.PASSED)
        assert lifecycle.transition(ProposalStatus.ACTIVE) is False
        assert lifecycle.current == ProposalStatus.PASSED

    def test_invalid_transition_passed_to_pending(self):
        """PASSED should not transition back to PENDING."""
        lifecycle = ProposalLifecycle()
        lifecycle.transition(ProposalStatus.PENDING)
        lifecycle.transition(ProposalStatus.ACTIVE)
        lifecycle.transition(ProposalStatus.PASSED)
        assert lifecycle.transition(ProposalStatus.PENDING) is False

    def test_lifecycle_snapshot(self):
        """Lifecycle snapshot should contain all fields."""
        lifecycle = ProposalLifecycle()
        lifecycle.transition(ProposalStatus.PENDING)
        lifecycle.transition(ProposalStatus.ACTIVE)
        snapshot = lifecycle.snapshot()
        assert snapshot["current"] == "active"
        assert snapshot["created_at"] is not None
        assert snapshot["activated_at"] is not None
        assert snapshot["resolved_at"] is None
        assert snapshot["executed_at"] is None
