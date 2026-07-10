from influx.consensus.coordination.vote import (
    Vote,
)

from influx.consensus.coordination.vote_state import (
    VoteState,
)


def create_vote():

    return Vote(
        vote_id="vote-1",
        proposal_id="proposal-1",
        validator="validator-1",
        approved=True,
    )


def test_vote_defaults():

    vote = create_vote()

    assert vote.vote_id == "vote-1"

    assert vote.approved

    assert (
        vote.state
        == VoteState.CREATED
    )


def test_cast():

    vote = create_vote()

    vote.cast()

    assert (
        vote.state
        == VoteState.CAST
    )


def test_verify():

    vote = create_vote()

    vote.verify()

    assert (
        vote.state
        == VoteState.VERIFIED
    )


def test_accept():

    vote = create_vote()

    vote.accept()

    assert (
        vote.state
        == VoteState.ACCEPTED
    )


def test_reject():

    vote = create_vote()

    vote.reject()

    assert (
        vote.state
        == VoteState.REJECTED
    )


def test_snapshot():

    vote = create_vote()

    snapshot = vote.snapshot()

    assert snapshot["vote_id"] == "vote-1"

    assert snapshot["proposal_id"] == "proposal-1"

    assert snapshot["validator"] == "validator-1"

    assert "state" in snapshot