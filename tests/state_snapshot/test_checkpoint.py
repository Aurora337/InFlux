from influx.state_snapshot.snapshot import (
    StateSnapshot,
)

from influx.state_snapshot.checkpoint import (
    Checkpoint,
)


def test_create_checkpoint():

    snapshot = StateSnapshot.create(
        10,
        {
            "alice": 100,
        },
    )

    checkpoint = Checkpoint.from_snapshot(
        snapshot
    )

    assert (
        checkpoint.height
        == 10
    )

    assert isinstance(
        checkpoint.snapshot_hash,
        str,
    )


def test_checkpoint_verification():

    snapshot = StateSnapshot.create(
        1,
        {
            "node": 1,
        },
    )

    checkpoint = Checkpoint.from_snapshot(
        snapshot
    )

    assert checkpoint.verify(
        snapshot
    )


def test_modified_snapshot_fails():

    snapshot = StateSnapshot.create(
        1,
        {
            "node": 1,
        },
    )

    checkpoint = Checkpoint.from_snapshot(
        snapshot
    )

    altered = StateSnapshot.create(
        1,
        {
            "node": 2,
        },
    )

    assert (
        checkpoint.verify(
            altered
        )
        is False
    )


def test_checkpoint_snapshot():

    checkpoint = Checkpoint(
        height=1,
        root_hash="root",
        snapshot_hash="hash",
    )

    result = checkpoint.snapshot()

    assert (
        "height"
        in result
    )

    assert (
        "root_hash"
        in result
    )

    assert (
        "snapshot_hash"
        in result
    )