from influx.network.discovery.discovery import (
    Discovery,
)

from influx.network.discovery.discovery_record import (
    DiscoveryRecord,
)

from influx.network.discovery.discovery_state import (
    DiscoveryState,
)


def create_record(
    node_id="node-1",
):
    return DiscoveryRecord(
        node_id=node_id,
        address="127.0.0.1",
        port=8080,
        trust_score=1.0,
    )


def test_discovery_defaults():

    discovery = Discovery()

    assert (
        discovery.state
        == DiscoveryState.INITIALIZING
    )


def test_start():

    discovery = Discovery()

    discovery.start()

    assert (
        discovery.state
        == DiscoveryState.DISCOVERING
    )


def test_discover_peer():

    discovery = Discovery()

    discovery.start()

    result = discovery.discover(
        create_record()
    )

    assert result

    assert (
        discovery.lookup("node-1")
        is not None
    )


def test_duplicate_peer():

    discovery = Discovery()

    record = create_record()

    discovery.discover(record)

    result = discovery.discover(record)

    assert not result


def test_remove_peer():

    discovery = Discovery()

    discovery.discover(
        create_record()
    )

    result = discovery.remove(
        "node-1"
    )

    assert result


def test_stop():

    discovery = Discovery()

    discovery.stop()

    assert (
        discovery.state
        == DiscoveryState.STOPPED
    )


def test_snapshot():

    discovery = Discovery()

    snapshot = discovery.snapshot()

    assert "state" in snapshot
    assert "metrics" in snapshot