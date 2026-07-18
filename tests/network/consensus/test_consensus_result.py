from influx.network.consensus.consensus_result import (
    ConsensusResult,
)


def test_defaults():
    result = ConsensusResult()

    assert not result.accepted


def test_snapshot():
    result = ConsensusResult()

    assert "accepted" in result.snapshot()