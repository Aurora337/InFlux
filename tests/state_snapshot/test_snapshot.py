from influx.state_snapshot.snapshot import (
    StateSnapshot,
)


def test_create_snapshot():

    snapshot = StateSnapshot.create(
        10,
        {
            "alice": 100,
            "bob": 50,
        },
    )

    assert (
        snapshot.height
        == 10
    )

    assert isinstance(
        snapshot.root_hash,
        str,
    )


def test_snapshot_verification():

    snapshot = StateSnapshot.create(
        1,
        {
            "node": 1,
        },
    )

    assert snapshot.verify()


def test_modified_state_fails_verification():

    snapshot = StateSnapshot.create(
        1,
        {
            "node": 1,
        },
    )

    snapshot.state["node"] = 2

    assert (
        snapshot.verify()
        is False
    )


def test_snapshot_output():

    snapshot = StateSnapshot.create(
        5,
        {
            "height": 5,
        },
    )

    result = snapshot.snapshot()

    assert (
        "height"
        in result
    )

    assert (
        "state"
        in result
    )

    assert (
        "root_hash"
        in result
    )