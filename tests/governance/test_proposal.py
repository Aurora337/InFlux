from influx.governance.proposal import (
    Proposal,
)


def test_proposal_creation():

    proposal = Proposal(
        proposal_id="upgrade-1",
        title="Protocol Upgrade",
        description="Upgrade consensus rules",
        proposer="node-1",
    )

    assert (
        proposal.proposal_id
        == "upgrade-1"
    )

    assert (
        proposal.active
        is True
    )

    assert (
        len(proposal.votes_for)
        == 0
    )


def test_approve_vote():

    proposal = Proposal(
        proposal_id="upgrade-1",
        title="Upgrade",
        description="Change protocol",
        proposer="node-1",
    )

    proposal.approve(
        "validator-1",
    )

    assert (
        "validator-1"
        in proposal.votes_for
    )

    assert (
        proposal.approved()
        is True
    )


def test_reject_vote():

    proposal = Proposal(
        proposal_id="upgrade-1",
        title="Upgrade",
        description="Change protocol",
        proposer="node-1",
    )

    proposal.reject(
        "validator-1",
    )

    assert (
        "validator-1"
        in proposal.votes_against
    )


def test_vote_switch():

    proposal = Proposal(
        proposal_id="upgrade-1",
        title="Upgrade",
        description="Change protocol",
        proposer="node-1",
    )

    proposal.approve(
        "validator-1",
    )

    proposal.reject(
        "validator-1",
    )

    assert (
        "validator-1"
        not in proposal.votes_for
    )

    assert (
        "validator-1"
        in proposal.votes_against
    )