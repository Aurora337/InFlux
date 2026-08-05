from influx.state_snapshot.snapshot import (
    StateSnapshot,
)

from influx.state_snapshot.snapshot_store import (
    SnapshotStore,
)


def test_save_snapshot():

    store = SnapshotStore()

    snapshot = StateSnapshot.create(
        1,
        {
            "alice": 100,
        },
    )

    checkpoint = store.save(
        snapshot
    )

    assert (
        checkpoint.height
        == 1
    )


def test_get_snapshot():

    store = SnapshotStore()

    snapshot = StateSnapshot.create(
        5,
        {
            "node": 1,
        },
    )

    store.save(
        snapshot
    )

    result = store.get_snapshot(
        5
    )

    assert result is not None

    assert (
        result.height
        == 5
    )


def test_get_checkpoint():

    store = SnapshotStore()

    snapshot = StateSnapshot.create(
        2,
        {
            "node": 2,
        },
    )

    store.save(
        snapshot
    )

    checkpoint = store.get_checkpoint(
        2
    )

    assert checkpoint is not None

    assert (
        checkpoint.height
        == 2
    )


def test_latest_snapshot():

    store = SnapshotStore()

    store.save(
        StateSnapshot.create(
            1,
            {
                "a": 1,
            },
        )
    )

    store.save(
        StateSnapshot.create(
            10,
            {
                "a": 10,
            },
        )
    )

    latest = store.latest()

    assert latest is not None

    assert (
        latest.height
        == 10
    )