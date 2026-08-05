from influx.consensus.coordination.proposal import (
    Proposal,
)

from influx.consensus.coordination.proposal_state import (
    ProposalState,
)


def create_proposal():

    return Proposal(
        proposal_id="proposal-1",
        proposer="node-1",
        payload={
            "value": 100,
        },
    )


def test_proposal_defaults():

    proposal = create_proposal()

    assert proposal.proposal_id == "proposal-1"

    assert (
        proposal.state
        == ProposalState.CREATED
    )


def test_submit():

    proposal = create_proposal()

    proposal.submit()

    assert (
        proposal.state
        == ProposalState.SUBMITTED
    )


def test_validate():

    proposal = create_proposal()

    proposal.validate()

    assert (
        proposal.state
        == ProposalState.VALIDATING
    )


def test_accept():

    proposal = create_proposal()

    proposal.accept()

    assert (
        proposal.state
        == ProposalState.ACCEPTED
    )


def test_reject():

    proposal = create_proposal()

    proposal.reject()

    assert (
        proposal.state
        == ProposalState.REJECTED
    )


def test_finalize():

    proposal = create_proposal()

    proposal.finalize()

    assert (
        proposal.state
        == ProposalState.FINALIZED
    )


def test_snapshot():

    proposal = create_proposal()

    snapshot = proposal.snapshot()

    assert snapshot["proposal_id"] == "proposal-1"

    assert snapshot["proposer"] == "node-1"

    assert "payload" in snapshot

    assert "state" in snapshot