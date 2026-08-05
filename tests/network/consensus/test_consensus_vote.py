from influx.network.consensus.consensus_vote import (
    ConsensusVote,
)


def test_defaults():
    vote = ConsensusVote(
        voter="node-1",
    )

    assert vote.approve


def test_snapshot():
    vote = ConsensusVote(
        voter="node-1",
    )

    assert "voter" in vote.snapshot()