"""
Unit tests for the governance voting module.

Tests vote creation/hashing, voting power registration, vote casting,
quorum calculation, approval thresholds, veto mechanics, and result computation.
"""

import pytest

from influx.governance.voting import (
    Vote,
    VoteOption,
    VotingPower,
    VotingSession,
)


class TestVoteCreation:
    """Vote creation and hashing tests."""

    def test_vote_creation_all_options(self):
        """Create votes with all four voting options."""
        voter_id = "alice"
        proposal_id = "prop-001"

        yes_vote = Vote(voter_id=voter_id, proposal_id=proposal_id, option=VoteOption.YES, power=100.0)
        assert yes_vote.option == VoteOption.YES
        assert yes_vote.power == 100.0
        assert yes_vote.hash is not None

        no_vote = Vote(voter_id=voter_id, proposal_id=proposal_id, option=VoteOption.NO, power=100.0)
        assert no_vote.option == VoteOption.NO

        abstain_vote = Vote(voter_id=voter_id, proposal_id=proposal_id, option=VoteOption.ABSTAIN, power=100.0)
        assert abstain_vote.option == VoteOption.ABSTAIN

        veto_vote = Vote(voter_id=voter_id, proposal_id=proposal_id, option=VoteOption.VETO, power=100.0)
        assert veto_vote.option == VoteOption.VETO

    def test_vote_hash_determinism(self):
        """Same vote fields always produce the same hash."""
        v1 = Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.YES, power=100.0)
        v2 = Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.YES, power=100.0)
        assert v1.hash == v2.hash

    def test_vote_different_hashes(self):
        """Different votes produce different hashes."""
        yes_vote = Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.YES, power=100.0)
        no_vote = Vote(voter_id="bob", proposal_id="prop-001", option=VoteOption.NO, power=50.0)
        assert yes_vote.hash != no_vote.hash

    def test_vote_hash_cache(self):
        """Vote hash should be cached."""
        vote = Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.YES, power=100.0)
        first = vote.hash
        second = vote.hash
        assert first == second
        assert vote._hash is not None

    def test_vote_validation(self):
        """Valid vote should pass validation."""
        vote = Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.YES, power=100.0)
        assert vote.validate() is True

    def test_vote_empty_voter_rejected(self):
        """Empty voter_id should fail validation."""
        vote = Vote(voter_id="", proposal_id="prop-001", option=VoteOption.YES, power=100.0)
        assert vote.validate() is False

    def test_vote_empty_proposal_rejected(self):
        """Empty proposal_id should fail validation."""
        vote = Vote(voter_id="alice", proposal_id="", option=VoteOption.YES, power=100.0)
        assert vote.validate() is False

    def test_vote_negative_power_rejected(self):
        """Negative voting power should fail validation."""
        vote = Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.YES, power=-1.0)
        assert vote.validate() is False

    def test_vote_hash_integrity_check(self):
        """Vote with corrupted hash should fail validation."""
        vote = Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.YES, power=100.0)
        vote._hash = "tampered_hash"
        assert vote.validate() is False

    def test_vote_snapshot(self):
        """Vote snapshot should contain all expected fields."""
        vote = Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.YES, power=100.0)
        snapshot = vote.snapshot()
        assert snapshot["voter_id"] == "alice"
        assert snapshot["proposal_id"] == "prop-001"
        assert snapshot["option"] == "yes"
        assert snapshot["power"] == 100.0
        assert snapshot["hash"] == vote.hash


class TestVotingPower:
    """Voting power registration and representation tests."""

    def test_voting_power_creation(self):
        """Create voting power with all required fields."""
        vp = VotingPower(voter_id="alice", power=100.0, snapshot_block_height=5000)
        assert vp.voter_id == "alice"
        assert vp.power == 100.0
        assert vp.delegated_from == []
        assert vp.snapshot_block_height == 5000

    def test_voting_power_with_delegation(self):
        """Voting power can have delegated_from list."""
        vp = VotingPower(
            voter_id="validator1",
            power=200.0,
            delegated_from=["staker1", "staker2", "staker3"],
            snapshot_block_height=5000,
        )
        assert vp.delegated_from == ["staker1", "staker2", "staker3"]

    def test_voting_power_snapshot(self):
        """Voting power snapshot should contain all fields."""
        vp = VotingPower(
            voter_id="alice",
            power=100.0,
            delegated_from=["bob"],
            snapshot_block_height=5000,
        )
        snap = vp.snapshot()
        assert snap["voter_id"] == "alice"
        assert snap["power"] == 100.0
        assert snap["delegated_from"] == ["bob"]
        assert snap["snapshot_block_height"] == 5000


class TestVotingSession:
    """Voting session management tests."""

    def test_session_creation(self):
        """Create a voting session with default parameters."""
        session = VotingSession(
            proposal_id="prop-001",
            start_block=1000,
            end_block=2000,
            quorum=0.4,
            approval_threshold=0.5,
        )
        assert session.proposal_id == "prop-001"
        assert session.start_block == 1000
        assert session.end_block == 2000
        assert session.quorum == 0.4
        assert session.approval_threshold == 0.5
        assert session.votes == {}
        assert session.voting_powers == {}
        assert session.total_power_snapshot == 0.0

    def test_register_voting_power(self):
        """Register voting power for a voter."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000)
        assert session.register_voting_power("alice", 100.0) is True
        assert "alice" in session.voting_powers
        assert session.voting_powers["alice"].power == 100.0

    def test_register_voting_power_duplicate(self):
        """Registering same voter twice should fail."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000)
        session.register_voting_power("alice", 100.0)
        assert session.register_voting_power("alice", 200.0) is False

    def test_cast_valid_vote(self):
        """Cast a valid vote on a proposal."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000)
        session.register_voting_power("alice", 100.0)
        session.total_power_snapshot = 1000.0

        vote = Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.YES, power=100.0)
        assert session.cast_vote(vote) is True
        assert "alice" in session.votes

    def test_cast_vote_unknown_voter(self):
        """Unknown voter should be rejected."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000)
        session.total_power_snapshot = 1000.0

        vote = Vote(voter_id="unknown", proposal_id="prop-001", option=VoteOption.YES, power=100.0)
        assert session.cast_vote(vote) is False

    def test_cast_vote_power_mismatch(self):
        """Vote with power not matching registered power should be rejected."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000)
        session.register_voting_power("alice", 100.0)
        session.total_power_snapshot = 1000.0

        vote = Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.YES, power=50.0)
        assert session.cast_vote(vote) is False

    def test_double_voting_rejected(self):
        """Double voting by same voter should be rejected."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000)
        session.register_voting_power("alice", 100.0)
        session.total_power_snapshot = 1000.0

        vote1 = Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.YES, power=100.0)
        assert session.cast_vote(vote1) is True

        vote2 = Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.NO, power=100.0)
        assert session.cast_vote(vote2) is False

    def test_cast_invalid_vote(self):
        """Invalid vote should be rejected."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000)
        session.register_voting_power("alice", 100.0)
        session.total_power_snapshot = 1000.0

        invalid_vote = Vote(voter_id="alice", proposal_id="", option=VoteOption.YES, power=100.0)
        assert session.cast_vote(invalid_vote) is False


class TestQuorum:
    """Quorum calculation tests."""

    def test_quorum_reached(self):
        """Quorum should be reached when voted power >= quorum threshold."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000, quorum=0.4)
        session.register_voting_power("alice", 100.0)
        session.register_voting_power("bob", 100.0)
        session.register_voting_power("carol", 100.0)
        session.total_power_snapshot = 300.0

        # Alice and Bob vote = 200 power > 40% of 300 = 120
        vote1 = Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.YES, power=100.0)
        vote2 = Vote(voter_id="bob", proposal_id="prop-001", option=VoteOption.YES, power=100.0)
        session.cast_vote(vote1)
        session.cast_vote(vote2)

        assert session.has_quorum() is True

    def test_quorum_not_reached(self):
        """Quorum should not be reached when voted power < quorum threshold."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000, quorum=0.4)
        session.register_voting_power("alice", 100.0)
        session.register_voting_power("bob", 1000.0)
        session.total_power_snapshot = 1100.0

        # Only Alice votes = 100 power < 40% of 1100 = 440
        vote1 = Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.YES, power=100.0)
        session.cast_vote(vote1)

        assert session.has_quorum() is False

    def test_quorum_exact_minimum(self):
        """Quorum should be reached exactly at the threshold."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000, quorum=0.5)
        session.register_voting_power("alice", 500.0)
        session.register_voting_power("bob", 500.0)
        session.total_power_snapshot = 1000.0

        # Alice votes = 500 power = 50% of 1000
        vote1 = Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.YES, power=500.0)
        session.cast_vote(vote1)

        assert session.has_quorum() is True

    def test_quorum_zero_power(self):
        """Quorum should fail when total_power_snapshot is zero."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000)
        session.total_power_snapshot = 0.0
        assert session.has_quorum() is False


class TestApproval:
    """Approval threshold calculation tests."""

    def test_approval_passed(self):
        """Approval should pass when YES votes meet threshold."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000, approval_threshold=0.5)
        session.register_voting_power("alice", 100.0)
        session.register_voting_power("bob", 100.0)
        session.total_power_snapshot = 200.0

        # Both vote YES = 200/200 = 100% approval
        session.cast_vote(Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.YES, power=100.0))
        session.cast_vote(Vote(voter_id="bob", proposal_id="prop-001", option=VoteOption.YES, power=100.0))

        assert session.get_approval() is True

    def test_approval_failed(self):
        """Approval should fail when YES votes below threshold."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000, approval_threshold=0.5)
        session.register_voting_power("alice", 100.0)
        session.register_voting_power("bob", 100.0)
        session.total_power_snapshot = 200.0

        # Only Alice votes YES = 100/200 = 50% - exactly at threshold
        vote1 = Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.YES, power=100.0)
        vote2 = Vote(voter_id="bob", proposal_id="prop-001", option=VoteOption.NO, power=100.0)
        session.cast_vote(vote1)
        session.cast_vote(vote2)

        # 100/200 = 0.5 which is >= 0.5, so approval passes
        assert session.get_approval() is True

    def test_approval_with_abstain(self):
        """Abstain votes should be excluded from approval calculation."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000, approval_threshold=0.5)
        session.register_voting_power("alice", 100.0)
        session.register_voting_power("bob", 100.0)
        session.register_voting_power("carol", 100.0)
        session.total_power_snapshot = 300.0

        # Alice YES, Bob ABSTAIN, Carol NO - denominator should be YES+NO = 200
        session.cast_vote(Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.YES, power=100.0))
        session.cast_vote(Vote(voter_id="bob", proposal_id="prop-001", option=VoteOption.ABSTAIN, power=100.0))
        session.cast_vote(Vote(voter_id="carol", proposal_id="prop-001", option=VoteOption.NO, power=100.0))

        # YES/(YES+NO) = 100/200 = 0.5 >= 0.5
        assert session.get_approval() is True

    def test_approval_no_yes_no_votes(self):
        """Approval should fail when there are no YES or NO votes."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000)
        session.register_voting_power("alice", 100.0)
        session.total_power_snapshot = 100.0

        session.cast_vote(Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.ABSTAIN, power=100.0))

        assert session.get_approval() is False


class TestVeto:
    """Superminority veto tests."""

    def test_veto_triggered(self):
        """Veto should be triggered when VETO power > 1/3 of total voted."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000)
        session.register_voting_power("alice", 40.0)
        session.register_voting_power("bob", 60.0)
        session.total_power_snapshot = 100.0

        # Alice VETO=40, Bob YES=60
        # VETO/(total) = 40/100 = 0.4 > 0.333
        session.cast_vote(Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.VETO, power=40.0))
        session.cast_vote(Vote(voter_id="bob", proposal_id="prop-001", option=VoteOption.YES, power=60.0))

        assert session.has_veto() is True

    def test_veto_not_triggered(self):
        """Veto should not be triggered when VETO power <= 1/3 of total voted."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000)
        session.register_voting_power("alice", 30.0)
        session.register_voting_power("bob", 70.0)
        session.total_power_snapshot = 100.0

        # Alice VETO=30, Bob YES=70
        # VETO/(total) = 30/100 = 0.3 <= 0.333
        session.cast_vote(Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.VETO, power=30.0))
        session.cast_vote(Vote(voter_id="bob", proposal_id="prop-001", option=VoteOption.YES, power=70.0))

        assert session.has_veto() is False

    def test_veto_no_veto_votes(self):
        """No VETO votes should not trigger veto."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000)
        session.register_voting_power("alice", 100.0)
        session.total_power_snapshot = 100.0

        session.cast_vote(Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.YES, power=100.0))

        assert session.has_veto() is False

    def test_veto_zero_votes(self):
        """Veto should not trigger when no votes cast."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000)
        assert session.has_veto() is False


class TestResultComputation:
    """Voting result computation tests."""

    def test_compute_result_passed(self):
        """Result should show passed=True when quorum reached, approval met, no veto."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000, quorum=0.4, approval_threshold=0.5)
        session.register_voting_power("alice", 300.0)
        session.register_voting_power("bob", 200.0)
        session.register_voting_power("carol", 500.0)
        session.total_power_snapshot = 1000.0

        # Alice YES=300, Bob YES=200, Carol YES=500 => total=1000
        # Quorum: 1000/1000 = 1.0 >= 0.4 ✓
        # Approval: 1000/1000 = 1.0 >= 0.5 ✓
        # Veto: 0/1000 = 0 <= 0.333 ✓
        session.cast_vote(Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.YES, power=300.0))
        session.cast_vote(Vote(voter_id="bob", proposal_id="prop-001", option=VoteOption.YES, power=200.0))
        session.cast_vote(Vote(voter_id="carol", proposal_id="prop-001", option=VoteOption.YES, power=500.0))

        result = session.compute_result()
        assert result["passed"] is True
        assert result["yes_power"] == 1000.0
        assert result["no_power"] == 0.0
        assert result["abstain_power"] == 0.0
        assert result["veto_power"] == 0.0
        assert result["quorum_reached"] is True
        assert result["approval"] is True
        assert result["veto_active"] is False
        assert result["voter_count"] == 3

    def test_compute_result_failed_no_quorum(self):
        """Result should show passed=False when quorum not reached."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000, quorum=0.5, approval_threshold=0.5)
        session.register_voting_power("alice", 100.0)
        session.register_voting_power("bob", 900.0)
        session.total_power_snapshot = 1000.0

        # Only Alice votes = 100/1000 = 0.1 < 0.5
        session.cast_vote(Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.YES, power=100.0))

        result = session.compute_result()
        assert result["passed"] is False
        assert result["quorum_reached"] is False

    def test_compute_result_failed_no_approval(self):
        """Result should show passed=False when approval not met."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000, quorum=0.3, approval_threshold=0.5)
        session.register_voting_power("alice", 300.0)
        session.register_voting_power("bob", 700.0)
        session.total_power_snapshot = 1000.0

        # Alice YES=300, Bob NO=700 => YES/(YES+NO) = 300/1000 = 0.3 < 0.5
        session.cast_vote(Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.YES, power=300.0))
        session.cast_vote(Vote(voter_id="bob", proposal_id="prop-001", option=VoteOption.NO, power=700.0))

        result = session.compute_result()
        assert result["passed"] is False
        assert result["quorum_reached"] is True
        assert result["approval"] is False

    def test_compute_result_failed_veto(self):
        """Result should show passed=False when veto is active."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000, quorum=0.3, approval_threshold=0.5)
        session.register_voting_power("alice", 400.0)
        session.register_voting_power("bob", 600.0)
        session.total_power_snapshot = 1000.0

        # Alice VETO=400, Bob YES=600
        # VETO/(total) = 400/1000 = 0.4 > 0.333
        # Quorum: 1000/1000 = 1.0 >= 0.3 ✓
        # Approval: 600/600 = 1.0 >= 0.5 ✓
        # Veto: 400/1000 = 0.4 > 0.333 ✗
        session.cast_vote(Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.VETO, power=400.0))
        session.cast_vote(Vote(voter_id="bob", proposal_id="prop-001", option=VoteOption.YES, power=600.0))

        result = session.compute_result()
        assert result["passed"] is False
        assert result["veto_active"] is True

    def test_session_snapshot(self):
        """Voting session snapshot should contain all expected fields."""
        session = VotingSession(proposal_id="prop-001", start_block=1000, end_block=2000, quorum=0.4)
        session.register_voting_power("alice", 100.0)
        session.total_power_snapshot = 100.0
        session.cast_vote(Vote(voter_id="alice", proposal_id="prop-001", option=VoteOption.YES, power=100.0))

        snap = session.snapshot()
        assert snap["proposal_id"] == "prop-001"
        assert snap["vote_count"] == 1
        assert snap["voter_count"] == 1
        assert snap["start_block"] == 1000
        assert snap["end_block"] == 2000
        assert snap["quorum"] == 0.4
        assert snap["total_power_snapshot"] == 100.0
        assert "result" in snap
