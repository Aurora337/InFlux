from influx.state_sync.state_diff import (
    StateDiff,
)

from influx.state_sync.state_reconstructor import (
    StateReconstructor,
)


def test_apply_added_state():

    reconstructor = StateReconstructor()

    result = reconstructor.apply(
        {},
        StateDiff(
            added={
                "alice": 100,
            }
        ),
    )

    assert (
        result["alice"]
        == 100
    )


def test_apply_modified_state():

    reconstructor = StateReconstructor()

    result = reconstructor.apply(
        {
            "alice": 100,
        },
        StateDiff(
            modified={
                "alice": 250,
            }
        ),
    )

    assert (
        result["alice"]
        == 250
    )


def test_apply_removed_state():

    reconstructor = StateReconstructor()

    result = reconstructor.apply(
        {
            "alice": 100,
        },
        StateDiff(
            removed=[
                "alice",
            ]
        ),
    )

    assert (
        "alice"
        not in result
    )


def test_verify_state():

    reconstructor = StateReconstructor()

    assert reconstructor.verify(
        {
            "node": 1,
        },
        {
            "node": 1,
        },
    )