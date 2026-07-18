from influx.network.discovery.discovery_manager import (
    DiscoveryManager,
)

from influx.network.discovery.discovery_record import (
    DiscoveryRecord,
)


def create_record(
    node_id: str = "node-1",
) -> DiscoveryRecord:

    return DiscoveryRecord(
        node_id=node_id,
        address="127.0.0.1",
        port=8080,
        role="validator",
    )


def test_register_peer():

    manager = DiscoveryManager()

    result = manager.register_peer(
        create_record()
    )

    assert result


def test_duplicate_peer():

    manager = DiscoveryManager()

    record = create_record()

    manager.register_peer(
        record
    )

    result = manager.register_peer(
        record
    )

    assert not result


def test_lookup_peer():

    manager = DiscoveryManager()

    record = create_record()

    manager.register_peer(
        record
    )

    found = manager.lookup(
        "node-1"
    )

    assert found is not None
    assert found.node_id == "node-1"


def test_remove_peer():

    manager = DiscoveryManager()

    manager.register_peer(
        create_record()
    )

    result = manager.remove_peer(
        "node-1"
    )

    assert result

    assert manager.lookup(
        "node-1"
    ) is None


def test_refresh_peer():

    manager = DiscoveryManager()

    manager.register_peer(
        create_record()
    )

    result = manager.refresh_peer(
        "node-1"
    )

    assert result


def test_snapshot():

    manager = DiscoveryManager()

    manager.register_peer(
        create_record()
    )

    snapshot = manager.snapshot()

    assert "node-1" in snapshot