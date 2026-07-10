from influx.network.discovery.discovery_record import (
    DiscoveryRecord,
)


def test_record_defaults():

    record = DiscoveryRecord(
        node_id="node-1",
        address="127.0.0.1",
        port=8080,
    )

    assert record.node_id == "node-1"
    assert record.active


def test_update_seen():

    record = DiscoveryRecord(
        node_id="node-1",
        address="127.0.0.1",
        port=8080,
    )

    original = record.last_seen

    record.update_seen()

    assert record.last_seen >= original


def test_deactivate():

    record = DiscoveryRecord(
        node_id="node-1",
        address="127.0.0.1",
        port=8080,
    )

    record.deactivate()

    assert not record.active


def test_activate():

    record = DiscoveryRecord(
        node_id="node-1",
        address="127.0.0.1",
        port=8080,
        active=False,
    )

    record.activate()

    assert record.active


def test_snapshot():

    record = DiscoveryRecord(
        node_id="node-1",
        address="localhost",
        port=9000,
        role="archive",
    )

    snapshot = record.snapshot()

    assert snapshot["node_id"] == "node-1"
    assert snapshot["role"] == "archive"