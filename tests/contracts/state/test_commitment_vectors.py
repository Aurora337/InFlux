from influx.contracts.state.snapshot import StateSnapshot
from influx.contracts.state.commitment import StateCommitment


def create_snapshot():
    return StateSnapshot(
        contract_id="contract_a",
        version="1.0.0",
        state={
            "balance": 100,
            "owner": "validator_001",
        },
        height=10,
    )


def test_commitment_generation():

    snapshot = create_snapshot()

    commitment = StateCommitment.generate(snapshot)

    assert len(commitment) == 64


def test_same_snapshot_same_commitment():

    first = create_snapshot()
    second = create_snapshot()

    assert (
        StateCommitment.generate(first)
        ==
        StateCommitment.generate(second)
    )


def test_different_state_changes_commitment():

    first = create_snapshot()

    second = StateSnapshot(
        contract_id="contract_a",
        version="1.0.0",
        state={
            "balance": 200,
            "owner": "validator_001",
        },
        height=10,
    )

    assert (
        StateCommitment.generate(first)
        !=
        StateCommitment.generate(second)
    )


def test_commitment_verification_passes():

    snapshot = create_snapshot()

    commitment = StateCommitment.generate(snapshot)

    assert StateCommitment.matches(
        snapshot,
        commitment,
    )


def test_invalid_commitment_fails():

    snapshot = create_snapshot()

    assert not StateCommitment.matches(
        snapshot,
        "invalid",
    )


def test_commitment_is_deterministic():

    snapshot = create_snapshot()

    first = StateCommitment.generate(snapshot)
    second = StateCommitment.generate(snapshot)

    assert first == second