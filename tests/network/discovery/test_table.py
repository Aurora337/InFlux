from influx.network.discovery.discovery_record import (
    DiscoveryRecord,
)

from influx.network.discovery.discovery_table import (
    DiscoveryTable,
)


def create_record(
    node_id="node-1",
):
    return DiscoveryRecord(
        node_id=node_id,
        address="127.0.0.1",
        port=8080,
    )


def test_add_record():

    table = DiscoveryTable()

    record = create_record()

    result = table.add(record)

    assert result
    assert table.count() == 1


def test_duplicate_record():

    table = DiscoveryTable()

    record = create_record()

    table.add(record)

    result = table.add(record)

    assert not result


def test_lookup():

    table = DiscoveryTable()

    record = create_record()

    table.add(record)

    found = table.lookup(
        "node-1"
    )

    assert found is record


def test_remove():

    table = DiscoveryTable()

    record = create_record()

    table.add(record)

    result = table.remove(
        "node-1"
    )

    assert result
    assert table.count() == 0


def test_active_peers():

    table = DiscoveryTable()

    active = create_record(
        "active-node",
    )

    inactive = create_record(
        "inactive-node",
    )

    inactive.deactivate()

    table.add(active)

    table.add(inactive)

    peers = table.active_peers()

    assert active in peers
    assert inactive not in peers


def test_snapshot():

    table = DiscoveryTable()

    table.add(
        create_record()
    )

    snapshot = table.snapshot()

    assert "node-1" in snapshot