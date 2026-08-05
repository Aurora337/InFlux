from influx.governance.proposal import (
    Proposal,
)

from influx.governance.voting_engine import (
    VoteResult,
    VotingEngine,
)


def test_vote_execution():

    proposal = Proposal(
        proposal_id="upgrade-1",
        title="Upgrade",
        description="Protocol change",
        proposer="node-1",
    )

    proposal.approve(
        "validator-1",
    )

    engine = VotingEngine()

    result = engine.vote(
        proposal
    )

    assert isinstance(
        result,
        VoteResult,
    )

    assert (
        result.approved
        is True
    )

    assert (
        result.votes_for
        == 1
    )


def test_failed_vote():

    proposal = Proposal(
        proposal_id="upgrade-1",
        title="Upgrade",
        description="Protocol change",
        proposer="node-1",
    )

    engine = VotingEngine()

    result = engine.vote(
        proposal,
        threshold=2,
    )

    assert (
        result.approved
        is False
    )


def test_vote_counts():

    proposal = Proposal(
        proposal_id="upgrade-1",
        title="Upgrade",
        description="Protocol change",
        proposer="node-1",
    )

    proposal.approve(
        "validator-1",
    )

    proposal.approve(
        "validator-2",
    )

    engine = VotingEngine()

    result = engine.vote(
        proposal,
    )

    assert (
        result.votes_for
        == 2
    )