from influx.state_snapshot.snapshot import (
    StateSnapshot,
)

from influx.state_snapshot.snapshot_store import (
    SnapshotStore,
)

from influx.state_snapshot.bootstrap import (
    BootstrapLoader,
)


def test_bootstrap_load():

    store = SnapshotStore()

    store.save(
        StateSnapshot.create(
            1,
            {
                "alice": 100,
            },
        )
    )

    loader = BootstrapLoader(
        store
    )

    state = loader.load(
        1
    )

    assert state is not None

    assert (
        state["alice"]
        == 100
    )


def test_bootstrap_missing_height():

    store = SnapshotStore()

    loader = BootstrapLoader(
        store
    )

    assert (
        loader.load(100)
        is None
    )


def test_latest_bootstrap():

    store = SnapshotStore()

    store.save(
        StateSnapshot.create(
            1,
            {
                "node": 1,
            },
        )
    )

    store.save(
        StateSnapshot.create(
            2,
            {
                "node": 2,
            },
        )
    )

    loader = BootstrapLoader(
        store
    )

    state = loader.latest()

    assert state is not None

    assert (
        state["node"]
        == 2
    )