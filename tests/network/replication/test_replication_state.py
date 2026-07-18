from influx.network.replication.replication_state import (
    ReplicationState,
)


def test_states_exist():
    assert (
        ReplicationState.INITIALIZING.value
        == "initializing"
    )