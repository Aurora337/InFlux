from influx.network_sync.peer_sync import (
    PeerSynchronizer,
    SyncRequest,
)


def test_sync_state():

    synchronizer = PeerSynchronizer()

    request = SyncRequest(
        height=12,
    )

    result = synchronizer.sync(
        request,
        {
            "alice": 500,
        },
    )

    assert result is True

    state = synchronizer.get(
        12
    )

    assert state is not None
    assert state["alice"] == 500


def test_missing_state():

    synchronizer = PeerSynchronizer()

    assert synchronizer.get(
        100
    ) is None


def test_synced_heights():

    synchronizer = PeerSynchronizer()

    synchronizer.sync(
        SyncRequest(3),
        {},
    )

    synchronizer.sync(
        SyncRequest(1),
        {},
    )

    synchronizer.sync(
        SyncRequest(2),
        {},
    )

    assert synchronizer.synced_heights() == [1, 2, 3]


def test_state_is_copied():

    synchronizer = PeerSynchronizer()

    original = {
        "balance": 100,
    }

    synchronizer.sync(
        SyncRequest(1),
        original,
    )

    original["balance"] = 999

    stored = synchronizer.get(1)

    assert stored is not None
    assert stored["balance"] == 100