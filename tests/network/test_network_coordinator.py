from influx.network.network_coordinator import NetworkCoordinator


def test_creation():

    coordinator = NetworkCoordinator()

    assert coordinator is not None


def test_connect_peer():

    coordinator = NetworkCoordinator()

    assert coordinator.connect_peer("node-a")


def test_disconnect_peer():

    coordinator = NetworkCoordinator()

    coordinator.connect_peer("node-a")

    assert coordinator.disconnect_peer("node-a")


def test_synchronize():

    coordinator = NetworkCoordinator()

    assert coordinator.synchronize()


def test_replicate():

    coordinator = NetworkCoordinator()

    assert coordinator.replicate()


def test_snapshot():

    coordinator = NetworkCoordinator()

    snapshot = coordinator.snapshot()

    assert "state" in snapshot
    assert "metrics" in snapshot
    assert "router" in snapshot