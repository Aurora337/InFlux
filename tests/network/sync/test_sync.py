from influx.network.sync.sync import Sync
from influx.network.sync.sync_session import SyncSession
from influx.network.sync.sync_state import SyncState


def test_connect():

    sync = Sync(
        sync_id="sync-1",
    )

    assert sync.connect()

    assert sync.state is SyncState.CONNECTING


def test_synchronize():

    sync = Sync(
        sync_id="sync-1",
    )

    sync.synchronize()

    assert sync.state is SyncState.SYNCHRONIZING


def test_complete():

    sync = Sync(
        sync_id="sync-1",
    )

    sync.complete()

    assert sync.state is SyncState.SYNCHRONIZED


def test_add_session():

    sync = Sync(
        sync_id="sync-1",
    )

    sync.add_session(
        SyncSession(
            session_id="s1",
            peer_id="node1",
        )
    )

    assert sync.session_count() == 1