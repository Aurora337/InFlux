from influx.state_sync.state_diff import (
    StateDiff,
    StateDiffGenerator,
)


def test_empty_diff():

    generator = StateDiffGenerator()

    diff = generator.compare(
        {
            "alice": 100,
        },
        {
            "alice": 100,
        },
    )

    assert isinstance(
        diff,
        StateDiff,
    )

    assert diff.is_empty()


def test_added_state():

    generator = StateDiffGenerator()

    diff = generator.compare(
        {},
        {
            "alice": 100,
        },
    )

    assert (
        diff.added["alice"]
        == 100
    )


def test_modified_state():

    generator = StateDiffGenerator()

    diff = generator.compare(
        {
            "alice": 100,
        },
        {
            "alice": 200,
        },
    )

    assert (
        diff.modified["alice"]
        == 200
    )


def test_removed_state():

    generator = StateDiffGenerator()

    diff = generator.compare(
        {
            "alice": 100,
        },
        {},
    )

    assert (
        "alice"
        in diff.removed
    )


def test_snapshot():

    diff = StateDiff(
        added={
            "node": 1,
        }
    )

    snapshot = diff.snapshot()

    assert (
        "added"
        in snapshot
    )

    assert (
        "modified"
        in snapshot
    )

    assert (
        "removed"
        in snapshot
    )