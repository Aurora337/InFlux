from influx.consensus.coordination.proposal import (
    Proposal,
)

from influx.consensus.coordination.consensus_round import (
    ConsensusRound,
)

from influx.consensus.coordination.round_manager import (
    RoundManager,
)


def create_round():

    proposal = Proposal(
        proposal_id="proposal-1",
        proposer="node-1",
        payload={
            "value": 10,
        },
    )

    return ConsensusRound(
        round_id="round-1",
        proposal=proposal,
    )


def test_round_defaults():

    round_instance = create_round()

    assert round_instance.round_id == "round-1"

    assert not round_instance.completed


def test_start_round():

    round_instance = create_round()

    round_instance.start()

    assert (
        round_instance.proposal.state.value
        == "validating"
    )


def test_finalize_round():

    round_instance = create_round()

    round_instance.finalize()

    assert round_instance.completed

    assert (
        round_instance.proposal.state.value
        == "finalized"
    )


def test_reject_round():

    round_instance = create_round()

    round_instance.reject()

    assert round_instance.completed

    assert (
        round_instance.proposal.state.value
        == "rejected"
    )


def test_round_manager_add():

    manager = RoundManager()

    result = manager.add(
        create_round()
    )

    assert result

    assert (
        manager.lookup("round-1")
        is not None
    )


def test_round_manager_duplicate():

    manager = RoundManager()

    round_instance = create_round()

    manager.add(
        round_instance
    )

    result = manager.add(
        round_instance
    )

    assert not result


def test_round_snapshot():

    snapshot = create_round().snapshot()

    assert snapshot["round_id"] == "round-1"

    assert "proposal" in snapshot