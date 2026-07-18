from influx.network.consensus.consensus_metrics import (
    ConsensusMetrics,
)


def test_defaults():
    metrics = ConsensusMetrics()

    assert metrics.rounds_started == 0


def test_snapshot():
    metrics = ConsensusMetrics()

    assert "votes_cast" in metrics.snapshot()