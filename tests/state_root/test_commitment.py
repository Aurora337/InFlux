from influx.state_root.state_commitment import (
    StateCommitment,
)


def test_create_commitment():

    commitment = StateCommitment.from_state(
        10,
        {
            "alice": 100,
        },
    )

    assert (
        commitment.height
        == 10
    )

    assert (
        commitment.state_size
        == 1
    )

    assert isinstance(
        commitment.root_hash,
        str,
    )


def test_verify_matching_state():

    state = {
        "alice": 100,
        "bob": 50,
    }

    commitment = StateCommitment.from_state(
        1,
        state,
    )

    assert commitment.verify(
        state
    )


def test_verify_modified_state():

    commitment = StateCommitment.from_state(
        1,
        {
            "alice": 100,
        },
    )

    assert (
        commitment.verify(
            {
                "alice": 200,
            }
        )
        is False
    )


def test_snapshot():

    commitment = StateCommitment.from_state(
        5,
        {
            "node": 1,
        },
    )

    snapshot = commitment.snapshot()

    assert (
        "height"
        in snapshot
    )

    assert (
        "root_hash"
        in snapshot
    )