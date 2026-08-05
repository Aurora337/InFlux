from influx.state_root.state_root import (
    StateRoot,
)


def test_state_root_generation():

    state = {
        "alice": 100,
        "bob": 50,
    }

    root = StateRoot(
        state
    )

    result = root.calculate()

    assert isinstance(
        result,
        str,
    )

    assert len(result) == 64


def test_state_ordering_is_deterministic():

    first = StateRoot(
        {
            "alice": 100,
            "bob": 50,
        }
    ).calculate()

    second = StateRoot(
        {
            "bob": 50,
            "alice": 100,
        }
    ).calculate()

    assert (
        first
        ==
        second
    )


def test_canonical_leaves():

    root = StateRoot(
        {
            "z": 1,
            "a": 2,
        }
    )

    leaves = root.canonical_leaves()

    assert leaves == [
        "a:2",
        "z:1",
    ]


def test_snapshot():

    root = StateRoot(
        {
            "node": 10,
        }
    )

    snapshot = root.snapshot()

    assert (
        "state"
        in snapshot
    )

    assert (
        "root"
        in snapshot
    )