"""
Performance baseline tests for the governance subsystem.

Records baseline execution times and memory usage for common governance
operations to detect regressions in future changes.
Not intended for optimization, just regression detection.
"""

import time

import pytest

from influx.governance.governance_engine import GovernanceEngine
from influx.governance.proposal import ProposalType, ProposalStatus, ProposalLifecycle
from influx.governance.voting import Vote, VoteOption, VotingSession
from influx.governance.treasury import Treasury


# Mark all tests in this module as performance tests
pytestmark = pytest.mark.slow


class TestPerformanceBaselines:
    """Baseline performance measurements for governance operations."""

    def test_proposal_creation_benchmark(self):
        """Measure time to create 100 proposals."""
        engine = GovernanceEngine()
        start = time.time()
        count = 100

        for i in range(count):
            engine.create_proposal(
                title=f"Performance Proposal {i}",
                description=f"Testing performance for proposal {i}",
                proposer=f"user{i % 10}",
            )

        elapsed = time.time() - start
        avg = elapsed / count
        print(f"\n  Created {count} proposals in {elapsed:.4f}s (avg {avg*1000:.2f}ms each)")

        # No strict threshold - just record baseline
        assert engine.metrics.proposals_created == count

    def test_vote_casting_benchmark(self):
        """Measure time to cast 1000 votes."""
        engine = GovernanceEngine(current_block_height=100)
        proposal = engine.create_proposal(
            title="Vote Benchmark",
            description="Benchmarking vote casting",
            proposer="alice",
            quorum=0.01,
        )
        engine.submit_proposal(proposal.proposal_id)
        engine.activate_proposal(proposal.proposal_id)

        session = engine.voting_sessions[proposal.proposal_id]
        count = 100
        start = time.time()

        for i in range(count):
            voter_id = f"voter_{i}"
            session.register_voting_power(voter_id, 1.0)
            engine.cast_vote(proposal.proposal_id, voter_id, VoteOption.YES, 1.0)

        elapsed = time.time() - start
        avg = elapsed / count
        print(f"\n  Cast {count} votes in {elapsed:.4f}s (avg {avg*1000:.2f}ms each)")

    def test_lifecycle_transitions_benchmark(self):
        """Measure time for 1000 lifecycle state transitions."""
        count = 1000
        start = time.time()

        for _ in range(count):
            lifecycle = ProposalLifecycle()
            lifecycle.transition(ProposalStatus.PENDING)
            lifecycle.transition(ProposalStatus.ACTIVE)
            lifecycle.transition(ProposalStatus.PASSED)
            lifecycle.transition(ProposalStatus.EXECUTED)

        elapsed = time.time() - start
        avg = elapsed / count
        print(f"\n  Completed {count} lifecycle sequences in {elapsed:.4f}s (avg {avg*1000:.2f}ms each)")

    def test_treasury_operations_benchmark(self):
        """Measure time for 1000 treasury operations."""
        treasury = Treasury()
        treasury.deposit("INFLUX", 1000000.0, "genesis")

        count = 1000
        start = time.time()

        for i in range(count):
            treasury.deposit("INFLUX", 100.0, "minter")
            treasury.withdraw("INFLUX", 50.0, f"user_{i}")

        elapsed = time.time() - start
        avg = elapsed / count
        print(f"\n  Completed {count} treasury operation pairs in {elapsed:.4f}s (avg {avg*1000:.2f}ms each)")

    def test_governance_snapshot_benchmark(self):
        """Measure time to compute governance snapshots."""
        engine = GovernanceEngine(current_block_height=100, execution_delay_blocks=0)
        engine.treasury.deposit("INFLUX", 100000.0, "genesis")

        # Create 10 proposals with votes
        for i in range(10):
            p = engine.create_proposal(
                title=f"Snapshot Benchmark {i}",
                description=f"Testing snapshot performance {i}",
                proposer=f"user{i}",
                quorum=0.3,
                proposal_type=ProposalType.TREASURY if i % 2 == 0 else ProposalType.TEXT,
                metadata={"amount": 1000.0, "recipient": "test", "token": "INFLUX"} if i % 2 == 0 else {},
            )
            engine.submit_proposal(p.proposal_id)
            engine.activate_proposal(p.proposal_id)

            for j in range(5):
                voter = f"voter_{i}_{j}"
                engine.cast_vote(p.proposal_id, voter, VoteOption.YES, 100.0)

            engine.close_voting(p.proposal_id)

        count = 100
        start = time.time()

        for _ in range(count):
            _ = engine.snapshot()

        elapsed = time.time() - start
        avg = elapsed / count
        print(f"\n  Computed {count} snapshots in {elapsed:.4f}s (avg {avg*1000:.2f}ms each)")

    def test_voting_result_computation_benchmark(self):
        """Measure time to compute voting results with many voters."""
        session = VotingSession(proposal_id="bench-prop", start_block=100, end_block=200, quorum=0.4)

        # Register 500 voters
        voter_count = 500
        for i in range(voter_count):
            session.register_voting_power(f"voter_{i}", 1.0)
        session.total_power_snapshot = float(voter_count)

        # Cast votes
        options = [VoteOption.YES, VoteOption.NO, VoteOption.ABSTAIN, VoteOption.VETO]
        for i in range(voter_count):
            option = options[i % 4]
            session.cast_vote(Vote(
                voter_id=f"voter_{i}",
                proposal_id="bench-prop",
                option=option,
                power=1.0,
            ))

        # Benchmark result computation
        count = 100
        start = time.time()

        for _ in range(count):
            _ = session.compute_result()

        elapsed = time.time() - start
        avg = elapsed / count
        print(f"\n  Computed {count} results for {voter_count} voters in {elapsed:.4f}s (avg {avg*1000:.2f}ms each)")
