"""
Unit tests for the governance metrics module.

Tests metrics recording, rate calculations, and snapshot behavior.
"""


from influx.governance.governance_metrics import GovernanceMetrics


class TestGovernanceMetricsInit:
    """Metrics initialization tests."""

    def test_metrics_initialization(self):
        """All counters should start at zero."""
        metrics = GovernanceMetrics()
        assert metrics.proposals_created == 0
        assert metrics.proposals_submitted == 0
        assert metrics.proposals_activated == 0
        assert metrics.proposals_passed == 0
        assert metrics.proposals_failed == 0
        assert metrics.proposals_executed == 0
        assert metrics.proposals_expired == 0
        assert metrics.proposals_vetoed == 0
        assert metrics.votes_cast == 0
        assert metrics.total_voting_power == 0.0
        assert metrics.governance_cycle_time_blocks == 0
        assert metrics.treasury_balance_influx == 0.0
        assert metrics.total_dispersed == 0.0
        assert metrics.total_deposited == 0.0


class TestMetricsRecording:
    """Metrics recording tests."""

    def test_record_proposal_created(self):
        """Recording proposal creation should increment counter."""
        metrics = GovernanceMetrics()
        metrics.record_proposal_created()
        assert metrics.proposals_created == 1
        metrics.record_proposal_created()
        metrics.record_proposal_created()
        assert metrics.proposals_created == 3

    def test_record_proposal_submitted(self):
        """Recording proposal submission should increment counter."""
        metrics = GovernanceMetrics()
        metrics.record_proposal_submitted()
        assert metrics.proposals_submitted == 1

    def test_record_proposal_activated(self):
        """Recording proposal activation should increment counter."""
        metrics = GovernanceMetrics()
        metrics.record_proposal_activated()
        assert metrics.proposals_activated == 1

    def test_record_proposal_passed(self):
        """Recording proposal passed should increment counter."""
        metrics = GovernanceMetrics()
        metrics.record_proposal_passed()
        assert metrics.proposals_passed == 1

    def test_record_proposal_failed(self):
        """Recording proposal failed should increment counter."""
        metrics = GovernanceMetrics()
        metrics.record_proposal_failed()
        assert metrics.proposals_failed == 1

    def test_record_proposal_executed(self):
        """Recording proposal execution should increment counter."""
        metrics = GovernanceMetrics()
        metrics.record_proposal_executed()
        assert metrics.proposals_executed == 1

    def test_record_vote_cast(self):
        """Recording vote cast should increment counter."""
        metrics = GovernanceMetrics()
        metrics.record_vote_cast()
        assert metrics.votes_cast == 1
        metrics.record_vote_cast()
        metrics.record_vote_cast()
        assert metrics.votes_cast == 3

    def test_all_records_independent(self):
        """All record methods should affect only their counter."""
        metrics = GovernanceMetrics()
        metrics.record_proposal_created()
        metrics.record_proposal_submitted()
        metrics.record_proposal_activated()
        metrics.record_proposal_passed()
        metrics.record_proposal_failed()
        metrics.record_proposal_executed()
        metrics.record_vote_cast()

        assert metrics.proposals_created == 1
        assert metrics.proposals_submitted == 1
        assert metrics.proposals_activated == 1
        assert metrics.proposals_passed == 1
        assert metrics.proposals_failed == 1
        assert metrics.proposals_executed == 1
        assert metrics.votes_cast == 1


class TestMetricsCalculations:
    """Metrics calculation tests."""

    def test_voting_participation_rate_no_proposals(self):
        """Participation rate should be 0 when no proposals activated."""
        metrics = GovernanceMetrics()
        assert metrics.compute_voting_participation_rate() == 0.0

    def test_voting_participation_rate_zero_participation(self):
        """Participation rate should be 0 when no proposals resolved."""
        metrics = GovernanceMetrics()
        metrics.proposals_activated = 10
        assert metrics.compute_voting_participation_rate() == 0.0

    def test_voting_participation_rate_full(self):
        """Participation rate should be 1.0 when all activated proposals resolved."""
        metrics = GovernanceMetrics()
        metrics.proposals_activated = 10
        metrics.proposals_passed = 6
        metrics.proposals_failed = 4
        rate = metrics.compute_voting_participation_rate()
        assert rate == 1.0  # (6+4)/10

    def test_voting_participation_rate_partial(self):
        """Participation rate should reflect partial resolution."""
        metrics = GovernanceMetrics()
        metrics.proposals_activated = 10
        metrics.proposals_passed = 3
        metrics.proposals_failed = 2
        rate = metrics.compute_voting_participation_rate()
        assert rate == 0.5  # (3+2)/10

    def test_proposal_success_rate_no_resolved(self):
        """Success rate should be 0 when no proposals resolved."""
        metrics = GovernanceMetrics()
        assert metrics.compute_proposal_success_rate() == 0.0

    def test_proposal_success_rate_all_passed(self):
        """Success rate should be 1.0 when all resolved proposals passed."""
        metrics = GovernanceMetrics()
        metrics.proposals_passed = 5
        metrics.proposals_failed = 0
        assert metrics.compute_proposal_success_rate() == 1.0

    def test_proposal_success_rate_mixed(self):
        """Success rate should reflect passed/total_resolved ratio."""
        metrics = GovernanceMetrics()
        metrics.proposals_passed = 7
        metrics.proposals_failed = 3
        rate = metrics.compute_proposal_success_rate()
        assert rate == 0.7  # 7/(7+3)


class TestMetricsSnapshot:
    """Metrics snapshot tests."""

    def test_snapshot_empty(self):
        """Empty metrics snapshot should reflect zero state."""
        metrics = GovernanceMetrics()
        snap = metrics.snapshot()
        assert snap["proposals_created"] == 0
        assert snap["votes_cast"] == 0
        assert snap["voting_participation_rate"] == 0.0
        assert snap["proposal_success_rate"] == 0.0

    def test_snapshot_with_data(self):
        """Snapshot should reflect recorded metrics."""
        metrics = GovernanceMetrics()
        metrics.record_proposal_created()
        metrics.record_proposal_created()
        metrics.record_proposal_submitted()
        metrics.record_proposal_activated()
        metrics.record_proposal_passed()
        metrics.record_vote_cast()
        metrics.record_vote_cast()
        metrics.record_vote_cast()

        snap = metrics.snapshot()
        assert snap["proposals_created"] == 2
        assert snap["proposals_submitted"] == 1
        assert snap["proposals_activated"] == 1
        assert snap["proposals_passed"] == 1
        assert snap["votes_cast"] == 3
