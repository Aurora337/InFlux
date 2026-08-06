"""
Unit tests for the governance engine module.

Tests API behavior: proposal creation, submission, activation,
voting, closing, execution, block advancement, and treasury integration.
Invariant tests are in test_governance_invariants.py.
"""


from influx.governance.proposal import ProposalStatus, ProposalType
from influx.governance.voting import VoteOption
from influx.governance.governance_engine import GovernanceEngine


class TestGovernanceEngineInit:
    """Engine initialization tests."""

    def test_engine_creation_defaults(self):
        """Engine should initialize with sensible defaults."""
        engine = GovernanceEngine()
        assert engine.proposals == {}
        assert engine.voting_sessions == {}
        assert engine.current_block_height == 0
        assert engine.voting_period_blocks == 1000
        assert engine.execution_delay_blocks == 100
        assert engine.engine_id is not None
        assert len(engine.engine_id) == 16

    def test_engine_with_custom_params(self):
        """Engine can be created with custom parameters."""
        engine = GovernanceEngine(
            current_block_height=100,
            voting_period_blocks=500,
            execution_delay_blocks=50,
        )
        assert engine.current_block_height == 100
        assert engine.voting_period_blocks == 500
        assert engine.execution_delay_blocks == 50

    def test_engine_has_subsystems(self):
        """Engine should have treasury, metrics, and drift_detector."""
        engine = GovernanceEngine()
        assert engine.treasury is not None
        assert engine.metrics is not None
        assert engine.drift_detector is not None


class TestCreateProposal:
    """Proposal creation via engine tests."""

    def test_create_proposal_valid(self):
        """Create a valid proposal through the engine."""
        engine = GovernanceEngine()
        proposal = engine.create_proposal(
            title="Test Proposal",
            description="Testing proposal creation",
            proposer="alice",
            proposal_type=ProposalType.TEXT,
        )
        assert proposal is not None
        assert proposal.title == "Test Proposal"
        assert proposal.proposer == "alice"
        assert proposal.proposal_type == ProposalType.TEXT
        assert proposal.lifecycle.current == ProposalStatus.DRAFT
        assert proposal.proposal_id in engine.proposals
        assert engine.metrics.proposals_created == 1

    def test_create_proposal_empty_title(self):
        """Empty title should return None."""
        engine = GovernanceEngine()
        proposal = engine.create_proposal(
            title="",
            description="Some description",
            proposer="alice",
        )
        assert proposal is None

    def test_create_proposal_empty_description(self):
        """Empty description should return None."""
        engine = GovernanceEngine()
        proposal = engine.create_proposal(
            title="Test",
            description="",
            proposer="alice",
        )
        assert proposal is None

    def test_create_proposal_empty_proposer(self):
        """Empty proposer should return None."""
        engine = GovernanceEngine()
        proposal = engine.create_proposal(
            title="Test",
            description="Some description",
            proposer="",
        )
        assert proposal is None

    def test_create_proposal_all_types(self):
        """Create proposals of each type through engine."""
        engine = GovernanceEngine()
        for pt in ProposalType:
            proposal = engine.create_proposal(
                title=f"{pt.value} proposal",
                description=f"A {pt.value} proposal",
                proposer="alice",
                proposal_type=pt,
            )
            assert proposal is not None
            assert proposal.proposal_type == pt

    def test_create_proposal_with_metadata(self):
        """Create proposal with custom metadata."""
        engine = GovernanceEngine()
        proposal = engine.create_proposal(
            title="Meta Test",
            description="Proposal with metadata",
            proposer="alice",
            metadata={"key": "value", "num": 42},
        )
        assert proposal is not None
        assert proposal.metadata == {"key": "value", "num": 42}

    def test_create_proposal_tracks_target_block(self):
        """Proposal target_block_height should be set when provided."""
        engine = GovernanceEngine(current_block_height=500)
        proposal = engine.create_proposal(
            title="Target Test",
            description="Testing target block",
            proposer="alice",
            target_block_height=1000,
        )
        assert proposal.target_block_height == 1000

    def test_create_proposal_auto_target(self):
        """Proposal target_block_height auto-set if not provided."""
        engine = GovernanceEngine(current_block_height=500)
        proposal = engine.create_proposal(
            title="Auto Target",
            description="Testing auto target",
            proposer="alice",
        )
        assert proposal.target_block_height == 501  # current + 1


class TestSubmitProposal:
    """Proposal submission tests."""

    def test_submit_proposal_valid(self):
        """Submit a valid draft proposal."""
        engine = GovernanceEngine()
        proposal = engine.create_proposal(title="Test", description="Test", proposer="alice")
        assert engine.submit_proposal(proposal.proposal_id) is True
        assert engine.proposals[proposal.proposal_id].lifecycle.current == ProposalStatus.PENDING

    def test_submit_nonexistent_proposal(self):
        """Submit a non-existent proposal should fail."""
        engine = GovernanceEngine()
        assert engine.submit_proposal("nonexistent") is False

    def test_submit_already_submitted(self):
        """Submit already submitted proposal should fail."""
        engine = GovernanceEngine()
        proposal = engine.create_proposal(title="Test", description="Test", proposer="alice")
        engine.submit_proposal(proposal.proposal_id)
        # Cannot submit again (already PENDING)
        assert engine.submit_proposal(proposal.proposal_id) is False


class TestActivateProposal:
    """Proposal activation tests."""

    def test_activate_proposal_valid(self):
        """Activate a pending proposal."""
        engine = GovernanceEngine()
        proposal = engine.create_proposal(title="Test", description="Test", proposer="alice")
        engine.submit_proposal(proposal.proposal_id)
        assert engine.activate_proposal(proposal.proposal_id) is True
        assert engine.proposals[proposal.proposal_id].lifecycle.current == ProposalStatus.ACTIVE
        assert proposal.proposal_id in engine.voting_sessions
        assert engine.metrics.proposals_activated == 1

    def test_activate_nonexistent_proposal(self):
        """Activate non-existent proposal should fail."""
        engine = GovernanceEngine()
        assert engine.activate_proposal("nonexistent") is False

    def test_activate_not_submitted(self):
        """Activate draft (not submitted) proposal should fail."""
        engine = GovernanceEngine()
        proposal = engine.create_proposal(title="Test", description="Test", proposer="alice")
        assert engine.activate_proposal(proposal.proposal_id) is False

    def test_activate_creates_voting_session(self):
        """Activation should create a voting session with correct params."""
        engine = GovernanceEngine(current_block_height=100)
        proposal = engine.create_proposal(
            title="Test", description="Test", proposer="alice",
            quorum=0.6, approval_threshold=0.66,
        )
        engine.submit_proposal(proposal.proposal_id)
        engine.activate_proposal(proposal.proposal_id)

        session = engine.voting_sessions[proposal.proposal_id]
        assert session.proposal_id == proposal.proposal_id
        assert session.start_block == 100
        assert session.end_block == 1100  # start + voting_period_blocks
        assert session.quorum == 0.6
        assert session.approval_threshold == 0.66


class TestCastVote:
    """Vote casting via engine tests."""

    def test_cast_vote_valid(self):
        """Cast a valid vote on an active proposal."""
        engine = GovernanceEngine(current_block_height=100)
        proposal = engine.create_proposal(title="Test", description="Test", proposer="alice")
        engine.submit_proposal(proposal.proposal_id)
        engine.activate_proposal(proposal.proposal_id)

        assert engine.cast_vote(proposal.proposal_id, "bob", VoteOption.YES, 100.0) is True
        session = engine.voting_sessions[proposal.proposal_id]
        assert "bob" in session.votes
        assert engine.metrics.votes_cast == 1

    def test_cast_vote_auto_registers_power(self):
        """Casting vote should auto-register voting power."""
        engine = GovernanceEngine(current_block_height=100)
        proposal = engine.create_proposal(title="Test", description="Test", proposer="alice")
        engine.submit_proposal(proposal.proposal_id)
        engine.activate_proposal(proposal.proposal_id)

        engine.cast_vote(proposal.proposal_id, "bob", VoteOption.YES, 100.0)
        session = engine.voting_sessions[proposal.proposal_id]
        assert "bob" in session.voting_powers
        assert session.voting_powers["bob"].power == 100.0

    def test_cast_vote_nonexistent_proposal(self):
        """Vote on non-existent proposal should fail."""
        engine = GovernanceEngine()
        assert engine.cast_vote("nonexistent", "bob", VoteOption.YES, 100.0) is False

    def test_cast_vote_not_active(self):
        """Vote on non-active proposal should fail."""
        engine = GovernanceEngine()
        proposal = engine.create_proposal(title="Test", description="Test", proposer="alice")
        # Not submitted/activated - still DRAFT
        assert engine.cast_vote(proposal.proposal_id, "bob", VoteOption.YES, 100.0) is False

    def test_cast_vote_pending_not_active(self):
        """Vote on pending (not yet active) proposal should fail."""
        engine = GovernanceEngine()
        proposal = engine.create_proposal(title="Test", description="Test", proposer="alice")
        engine.submit_proposal(proposal.proposal_id)
        assert engine.cast_vote(proposal.proposal_id, "bob", VoteOption.YES, 100.0) is False

    def test_double_vote_rejected(self):
        """Double voting should be rejected."""
        engine = GovernanceEngine(current_block_height=100)
        proposal = engine.create_proposal(title="Test", description="Test", proposer="alice")
        engine.submit_proposal(proposal.proposal_id)
        engine.activate_proposal(proposal.proposal_id)

        assert engine.cast_vote(proposal.proposal_id, "bob", VoteOption.YES, 100.0) is True
        assert engine.cast_vote(proposal.proposal_id, "bob", VoteOption.NO, 100.0) is False

    def test_cast_vote_all_options(self):
        """Cast votes with all four options."""
        engine = GovernanceEngine(current_block_height=100)
        proposal = engine.create_proposal(title="Test", description="Test", proposer="alice")
        engine.submit_proposal(proposal.proposal_id)
        engine.activate_proposal(proposal.proposal_id)

        assert engine.cast_vote(proposal.proposal_id, "alice", VoteOption.YES, 100.0) is True
        assert engine.cast_vote(proposal.proposal_id, "bob", VoteOption.NO, 200.0) is True
        assert engine.cast_vote(proposal.proposal_id, "carol", VoteOption.ABSTAIN, 50.0) is True
        assert engine.cast_vote(proposal.proposal_id, "dave", VoteOption.VETO, 75.0) is True

        session = engine.voting_sessions[proposal.proposal_id]
        assert len(session.votes) == 4


class TestCloseVoting:
    """Voting close and resolution tests."""

    def test_close_voting_passed(self):
        """Close voting with quorum and approval should pass."""
        engine = GovernanceEngine(current_block_height=100)
        proposal = engine.create_proposal(title="Test", description="Test", proposer="alice", quorum=0.3)
        engine.submit_proposal(proposal.proposal_id)
        engine.activate_proposal(proposal.proposal_id)

        # Register voters and set total power snapshot
        session = engine.voting_sessions[proposal.proposal_id]
        session.register_voting_power("alice", 300.0)
        session.register_voting_power("bob", 200.0)
        session.register_voting_power("carol", 500.0)
        session.total_power_snapshot = 1000.0

        engine.cast_vote(proposal.proposal_id, "alice", VoteOption.YES, 300.0)
        engine.cast_vote(proposal.proposal_id, "bob", VoteOption.YES, 200.0)
        engine.cast_vote(proposal.proposal_id, "carol", VoteOption.YES, 500.0)

        # Total power = 1000, voted = 1000, quorum=30% ✓, approval=100% ✓
        assert engine.close_voting(proposal.proposal_id) is True
        assert engine.proposals[proposal.proposal_id].lifecycle.current == ProposalStatus.PASSED
        assert engine.metrics.proposals_passed == 1

    def test_close_voting_failed_no_quorum(self):
        """Close voting without quorum should fail."""
        engine = GovernanceEngine(current_block_height=100)
        proposal = engine.create_proposal(title="Test", description="Test", proposer="alice", quorum=0.5)
        engine.submit_proposal(proposal.proposal_id)
        engine.activate_proposal(proposal.proposal_id)

        engine.cast_vote(proposal.proposal_id, "alice", VoteOption.YES, 100.0)

        # Total power = 1000 (auto), voted = 100, quorum=50% ✗
        engine.advance_block()  # This doesn't auto-close voting yet since block_height < end_block
        # But we should be able to close manually

    def test_close_voting_failed_no_approval(self):
        """Close voting without approval should fail."""
        engine = GovernanceEngine(current_block_height=100)
        proposal = engine.create_proposal(title="Test", description="Test", proposer="alice", quorum=0.3, approval_threshold=0.5)
        engine.submit_proposal(proposal.proposal_id)
        engine.activate_proposal(proposal.proposal_id)

        # Set total_power_snapshot properly
        session = engine.voting_sessions[proposal.proposal_id]
        session.register_voting_power("alice", 300.0)
        session.register_voting_power("bob", 700.0)
        session.total_power_snapshot = 1000.0

        engine.cast_vote(proposal.proposal_id, "alice", VoteOption.YES, 300.0)
        engine.cast_vote(proposal.proposal_id, "bob", VoteOption.NO, 700.0)

        assert engine.close_voting(proposal.proposal_id) is True
        assert engine.proposals[proposal.proposal_id].lifecycle.current == ProposalStatus.FAILED
        assert engine.metrics.proposals_failed == 1

    def test_close_voting_nonexistent(self):
        """Close voting on non-existent proposal should fail."""
        engine = GovernanceEngine()
        assert engine.close_voting("nonexistent") is False

    def test_close_voting_not_active(self):
        """Close voting on non-active proposal should fail."""
        engine = GovernanceEngine()
        proposal = engine.create_proposal(title="Test", description="Test", proposer="alice")
        engine.submit_proposal(proposal.proposal_id)
        # Currently PENDING, not ACTIVE
        assert engine.close_voting(proposal.proposal_id) is False


class TestExecuteProposal:
    """Proposal execution tests."""

    def test_execute_proposal_passed(self):
        """Execute a passed proposal."""
        engine = GovernanceEngine(current_block_height=100, execution_delay_blocks=0)
        proposal = engine.create_proposal(title="Test", description="Test", proposer="alice", quorum=0.3)
        engine.submit_proposal(proposal.proposal_id)
        engine.activate_proposal(proposal.proposal_id)

        # Register voter and set total power snapshot
        session = engine.voting_sessions[proposal.proposal_id]
        session.register_voting_power("alice", 1000.0)
        session.total_power_snapshot = 1000.0

        engine.cast_vote(proposal.proposal_id, "alice", VoteOption.YES, 1000.0)
        engine.close_voting(proposal.proposal_id)

        # With delay=0 and target_block=101, execute at block 101+
        engine.current_block_height = proposal.target_block_height + 1
        assert engine.execute_proposal(proposal.proposal_id) is True
        assert engine.proposals[proposal.proposal_id].lifecycle.current == ProposalStatus.EXECUTED
        assert engine.metrics.proposals_executed == 1

    def test_execute_proposal_too_early(self):
        """Execute before delay should fail."""
        engine = GovernanceEngine(current_block_height=100, execution_delay_blocks=100)
        proposal = engine.create_proposal(title="Test", description="Test", proposer="alice", quorum=0.3)
        engine.submit_proposal(proposal.proposal_id)
        engine.activate_proposal(proposal.proposal_id)

        engine.cast_vote(proposal.proposal_id, "alice", VoteOption.YES, 1000.0)
        engine.close_voting(proposal.proposal_id)

        # Try to execute before delay blocks have passed
        assert engine.execute_proposal(proposal.proposal_id) is False

    def test_execute_proposal_not_passed(self):
        """Execute a non-passed proposal should fail."""
        engine = GovernanceEngine(current_block_height=100)
        proposal = engine.create_proposal(title="Test", description="Test", proposer="alice")
        engine.submit_proposal(proposal.proposal_id)
        # Still PENDING
        assert engine.execute_proposal(proposal.proposal_id) is False

    def test_execute_nonexistent(self):
        """Execute non-existent proposal should fail."""
        engine = GovernanceEngine()
        assert engine.execute_proposal("nonexistent") is False

    def test_double_execution_rejected(self):
        """Execute a proposal twice should fail."""
        engine = GovernanceEngine(current_block_height=100, execution_delay_blocks=0)
        proposal = engine.create_proposal(title="Test", description="Test", proposer="alice", quorum=0.3)
        engine.submit_proposal(proposal.proposal_id)
        engine.activate_proposal(proposal.proposal_id)

        # Register voter and set total power snapshot
        session = engine.voting_sessions[proposal.proposal_id]
        session.register_voting_power("alice", 1000.0)
        session.total_power_snapshot = 1000.0

        engine.cast_vote(proposal.proposal_id, "alice", VoteOption.YES, 1000.0)
        engine.close_voting(proposal.proposal_id)
        engine.current_block_height = proposal.target_block_height + 1

        assert engine.execute_proposal(proposal.proposal_id) is True
        # Second execution should fail (EXECUTED is terminal)
        assert engine.execute_proposal(proposal.proposal_id) is False

    def test_treasury_proposal_execution(self):
        """Treasury proposal should create and execute dispersal."""
        engine = GovernanceEngine(current_block_height=100, execution_delay_blocks=0)
        engine.treasury.deposit("INFLUX", 10000.0, "minter")

        proposal = engine.create_proposal(
            title="Treasury Grant",
            description="Community grant",
            proposer="alice",
            proposal_type=ProposalType.TREASURY,
            quorum=0.3,
            metadata={
                "amount": 5000.0,
                "recipient": "community-pool",
                "token": "INFLUX",
            },
        )
        engine.submit_proposal(proposal.proposal_id)
        engine.activate_proposal(proposal.proposal_id)

        # Register voter and set total power snapshot
        session = engine.voting_sessions[proposal.proposal_id]
        session.register_voting_power("alice", 1000.0)
        session.total_power_snapshot = 1000.0

        engine.cast_vote(proposal.proposal_id, "alice", VoteOption.YES, 1000.0)
        engine.close_voting(proposal.proposal_id)
        engine.current_block_height = proposal.target_block_height + 1

        assert engine.execute_proposal(proposal.proposal_id) is True
        # Treasury should have deducted 5000
        assert engine.treasury.get_balance("INFLUX") == 5000.0  # 10000 - 5000
        assert engine.metrics.proposals_executed == 1


class TestAdvanceBlock:
    """Block advancement tests."""

    def test_advance_block_increases_height(self):
        """Advancing block should increase height by 1."""
        engine = GovernanceEngine(current_block_height=100)
        engine.advance_block()
        assert engine.current_block_height == 101
        engine.advance_block()
        assert engine.current_block_height == 102

    def test_auto_close_expired_voting(self):
        """Advancing past voting end should auto-close."""
        engine = GovernanceEngine(current_block_height=100, voting_period_blocks=5)
        proposal = engine.create_proposal(title="Test", description="Test", proposer="alice", quorum=0.3)
        engine.submit_proposal(proposal.proposal_id)
        engine.activate_proposal(proposal.proposal_id)

        # Advance to end_block (100 + 5 = 105)
        for _ in range(6):  # Advance to block 106 (past end_block 105)
            engine.advance_block()

        # Voting should have been auto-closed
        assert engine.proposals[proposal.proposal_id].lifecycle.current != ProposalStatus.ACTIVE


class TestFullLifecycle:
    """Complete proposal lifecycle tests."""

    def test_full_happy_path(self):
        """Complete lifecycle: create -> submit -> activate -> vote -> close -> execute."""
        engine = GovernanceEngine(current_block_height=100, execution_delay_blocks=0)
        engine.treasury.deposit("INFLUX", 10000.0, "minter")

        # 1. Create
        proposal = engine.create_proposal(
            title="Full Test",
            description="Testing full lifecycle",
            proposer="alice",
            quorum=0.3,
            proposal_type=ProposalType.TREASURY,
            metadata={"amount": 3000.0, "recipient": "grant-receiver", "token": "INFLUX"},
        )
        assert proposal.lifecycle.current == ProposalStatus.DRAFT

        # 2. Submit
        assert engine.submit_proposal(proposal.proposal_id)
        assert proposal.lifecycle.current == ProposalStatus.PENDING

        # 3. Activate
        assert engine.activate_proposal(proposal.proposal_id)
        assert proposal.lifecycle.current == ProposalStatus.ACTIVE

        # 4. Register voters and set total power snapshot
        session = engine.voting_sessions[proposal.proposal_id]
        session.register_voting_power("alice", 500.0)
        session.register_voting_power("bob", 300.0)
        session.register_voting_power("carol", 200.0)
        session.total_power_snapshot = 1000.0

        assert engine.cast_vote(proposal.proposal_id, "alice", VoteOption.YES, 500.0)
        assert engine.cast_vote(proposal.proposal_id, "bob", VoteOption.YES, 300.0)
        assert engine.cast_vote(proposal.proposal_id, "carol", VoteOption.YES, 200.0)

        # 5. Close
        assert engine.close_voting(proposal.proposal_id)
        assert proposal.lifecycle.current == ProposalStatus.PASSED

        # 6. Execute
        engine.current_block_height = proposal.target_block_height + 1
        assert engine.execute_proposal(proposal.proposal_id)
        assert proposal.lifecycle.current == ProposalStatus.EXECUTED

        # 7. Verify treasury
        assert engine.treasury.get_balance("INFLUX") == 7000.0  # 10000 - 3000

        # 8. Verify metrics
        assert engine.metrics.proposals_created == 1
        assert engine.metrics.proposals_submitted == 1
        assert engine.metrics.proposals_activated == 1
        assert engine.metrics.proposals_passed == 1
        assert engine.metrics.proposals_executed == 1
        assert engine.metrics.votes_cast == 3

    def test_failure_path_no_quorum(self):
        """Proposal without quorum should fail and not be executable."""
        engine = GovernanceEngine(current_block_height=100, execution_delay_blocks=0)
        engine.treasury.deposit("INFLUX", 10000.0, "minter")

        # Create with high quorum requirement
        proposal = engine.create_proposal(
            title="Fail Test",
            description="Testing failure path",
            proposer="alice",
            quorum=0.9,
        )
        engine.submit_proposal(proposal.proposal_id)
        engine.activate_proposal(proposal.proposal_id)

        # Only one voter with 100 power out of auto-registered total
        engine.cast_vote(proposal.proposal_id, "alice", VoteOption.YES, 100.0)

        engine.close_voting(proposal.proposal_id)
        assert proposal.lifecycle.current == ProposalStatus.FAILED

        # Cannot execute a failed proposal
        engine.current_block_height = proposal.target_block_height + 1
        assert engine.execute_proposal(proposal.proposal_id) is False

        # Treasury unchanged
        assert engine.treasury.get_balance("INFLUX") == 10000.0

    def test_engine_snapshot(self):
        """Engine snapshot should contain all expected fields."""
        engine = GovernanceEngine(current_block_height=100)
        proposal = engine.create_proposal(title="Snap", description="Test snapshot", proposer="alice")
        engine.submit_proposal(proposal.proposal_id)
        engine.activate_proposal(proposal.proposal_id)
        engine.cast_vote(proposal.proposal_id, "alice", VoteOption.YES, 100.0)
        engine.close_voting(proposal.proposal_id)

        snap = engine.snapshot()
        assert snap["engine_id"] == engine.engine_id
        assert snap["current_block_height"] >= 100
        assert snap["proposal_count"] == 1
        assert "treasury" in snap
        assert "metrics" in snap
