from influx.network.consensus.consensus_round import (
    ConsensusRound,
)
from influx.network.consensus.consensus_vote import (
    ConsensusVote,
)


def test_add_vote():
    round_ = ConsensusRound()

    assert round_.add_vote(
        ConsensusVote(
            voter="node-1",
        )
    )


def test_duplicate_vote():
    round_ = ConsensusRound()

    vote = ConsensusVote(
        voter="node-1",
    )

    round_.add_vote(vote)

    assert not round_.add_vote(vote)


def test_vote_totals():
    round_ = ConsensusRound()

    round_.add_vote(
        ConsensusVote(
            voter="A",
            approve=True,
        )
    )

    round_.add_vote(
        ConsensusVote(
            voter="B",
            approve=False,
        )
    )

    assert round_.approvals() == 1
    assert round_.rejections() == 1


def test_snapshot():
    round_ = ConsensusRound()

    assert "votes" in round_.snapshot()