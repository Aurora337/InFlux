from influx.network.cluster.cluster_state import ClusterState


def test_default_state() -> None:
    state = ClusterState()

    assert not state.active
    assert state.member_count == 0
    assert not state.synchronized