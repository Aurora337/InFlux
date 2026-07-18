from influx.network.sync.sync_state import SyncState


def test_states():

    assert (
        SyncState.SYNCHRONIZED.value
        == "synchronized"
    )