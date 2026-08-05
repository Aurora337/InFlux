from influx.consensus.coordination.consensus_validator import (
    ConsensusValidator,
)

from influx.consensus.coordination.proposal import (
    Proposal,
)

from influx.consensus.coordination.vote import (
    Vote,
)

from influx.consensus.coordination.proposal_state import (
    ProposalState,
)

from influx.consensus.coordination.vote_state import (
    VoteState,
)


def test_valid_proposal():

    validator = ConsensusValidator()

    proposal = Proposal(
        proposal_id="proposal-1",
        proposer="node-1",
        payload={},
    )

    assert validator.validate_proposal(
        proposal
    )


def test_invalid_proposal():

    validator = ConsensusValidator()

    proposal = Proposal(
        proposal_id="",
        proposer="node-1",
        payload={},
    )

    assert not validator.validate_proposal(
        proposal
    )


def test_valid_vote():

    validator = ConsensusValidator()

    vote = Vote(
        vote_id="vote-1",
        proposal_id="proposal-1",
        validator="node-1",
        approved=True,
    )

    assert validator.validate_vote(
        vote
    )


def test_invalid_vote():

    validator = ConsensusValidator()

    vote = Vote(
        vote_id="",
        proposal_id="proposal-1",
        validator="node-1",
        approved=True,
    )

    assert not validator.validate_vote(
        vote
    )


def test_valid_proposal_transition():

    validator = ConsensusValidator()

    assert validator.validate_transition(
        ProposalState.CREATED,
        ProposalState.SUBMITTED,
    )


def test_invalid_proposal_transition():

    validator = ConsensusValidator()

    assert not validator.validate_transition(
        ProposalState.CREATED,
        ProposalState.FINALIZED,
    )


def test_valid_vote_transition():

    validator = ConsensusValidator()

    assert validator.validate_vote_state(
        VoteState.CREATED,
        VoteState.CAST,
    )