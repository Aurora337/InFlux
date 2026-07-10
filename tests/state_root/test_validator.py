from influx.state_root.root_validator import (
    RootValidator,
)

from influx.state_root.state_commitment import (
    StateCommitment,
)


def test_validate_state():

    state = {
        "alice": 100,
    }

    commitment = StateCommitment.from_state(
        1,
        state,
    )

    validator = RootValidator()

    assert validator.validate(
        commitment,
        state,
    )


def test_reject_invalid_state():

    commitment = StateCommitment.from_state(
        1,
        {
            "alice": 100,
        },
    )

    validator = RootValidator()

    assert (
        validator.validate(
            commitment,
            {
                "alice": 50,
            },
        )
        is False
    )


def test_compare_matching_roots():

    state = {
        "node": 10,
    }

    first = StateCommitment.from_state(
        1,
        state,
    )

    second = StateCommitment.from_state(
        1,
        state,
    )

    validator = RootValidator()

    assert validator.compare(
        first,
        second,
    )


def test_snapshot():

    validator = RootValidator()

    snapshot = validator.snapshot()

    assert (
        snapshot["status"]
        == "active"
    )