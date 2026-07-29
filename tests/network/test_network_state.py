from influx.network.network_state import NetworkState


def test_state_creation():

    state = NetworkState()

    assert state.network_id == "influx-network"
    assert state.epoch == 0



def test_add_peer():

    state = NetworkState()

    state.add_peer(
        "node-a"
    )

    assert state.peer_count() == 1



def test_remove_peer():

    state = NetworkState()

    state.add_peer(
        "node-a"
    )

    state.remove_peer(
        "node-a"
    )

    assert state.peer_count() == 0



def test_sync_cycle():

    state = NetworkState()

    state.start_sync()

    assert state.sync_active
    assert state.sync_round == 1

    state.complete_sync()

    assert not state.sync_active



def test_replication_cycle():

    state = NetworkState()

    state.start_replication()

    assert state.replication_active
    assert state.replication_round == 1

    state.complete_replication()

    assert not state.replication_active



def test_epoch_increment():

    state = NetworkState()

    state.increment_epoch()

    assert state.epoch == 1



def test_snapshot():

    state = NetworkState()

    state.add_peer(
        "node-a"
    )

    snapshot = state.snapshot()

    assert snapshot["peer_count"] == 1