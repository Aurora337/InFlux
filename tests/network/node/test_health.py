from influx.network.node.node_health import NodeHealth
from influx.network.node.node_state import NodeState


def test_default_health():

    health = NodeHealth()

    assert health.state == NodeState.CREATED
    assert not health.healthy()


def test_ready():

    health = NodeHealth()

    health.transport_ready = True

    assert health.ready()


def test_failed_not_ready():

    health = NodeHealth(
        state=NodeState.FAILED
    )

    assert not health.ready()


def test_healthy():

    health = NodeHealth(
        state=NodeState.ACTIVE,
        transport_ready=True,
        sync_complete=True,
    )

    assert health.healthy()


def test_snapshot():

    health = NodeHealth()

    snapshot = health.snapshot()

    assert "state" in snapshot
    assert "healthy" in snapshot