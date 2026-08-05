from influx.consensus.coordination.consensus_metrics import (
    ConsensusMetrics,
)


def test_record_proposal():

    metrics = ConsensusMetrics()

    metrics.record_proposal()

    assert metrics.proposals_created == 1


def test_record_accept():

    metrics = ConsensusMetrics()

    metrics.record_accept()

    assert metrics.proposals_accepted == 1


def test_record_reject():

    metrics = ConsensusMetrics()

    metrics.record_reject()

    assert metrics.proposals_rejected == 1


def test_record_vote():

    metrics = ConsensusMetrics()

    metrics.record_vote()

    assert metrics.votes_received == 1


def test_record_vote_accept():

    metrics = ConsensusMetrics()

    metrics.record_vote_accept()

    assert metrics.votes_accepted == 1


def test_round_complete():

    metrics = ConsensusMetrics()

    metrics.record_round_complete()

    assert metrics.rounds_completed == 1


def test_failure():

    metrics = ConsensusMetrics()

    metrics.record_failure()

    assert metrics.validation_failures == 1


def test_snapshot():

    metrics = ConsensusMetrics()

    snapshot = metrics.snapshot()

    assert "votes_received" in snapshot

    assert "rounds_completed" in snapshot