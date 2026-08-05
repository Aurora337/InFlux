from influx.network.cluster.cluster_state import ClusterState


def test_initializing_state() -> None:
    assert ClusterState.INITIALIZING.value == "initializing"


def test_active_state() -> None:
    assert ClusterState.ACTIVE.value == "active"


def test_state_transitions() -> None:
    assert ClusterState.FORMING.value == "forming"
    assert ClusterState.DEGRADED.value == "degraded"
    assert ClusterState.RECOVERING.value == "recovering"
    assert ClusterState.STOPPED.value == "stopped"
    assert ClusterState.FAILED.value == "failed"
