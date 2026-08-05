from influx.interoperability.bridge import (
    BridgeConnection,
    InteroperabilityBridge,
)


def test_create_bridge():

    bridge = InteroperabilityBridge()

    connection = bridge.connect(
        source_network="cluster-a",
        destination_network="cluster-b",
    )

    assert isinstance(
        connection,
        BridgeConnection,
    )

    assert (
        connection.source_network
        == "cluster-a"
    )

    assert (
        connection.destination_network
        == "cluster-b"
    )

    assert (
        connection.active
        is True
    )


def test_bridge_registry():

    bridge = InteroperabilityBridge()

    bridge.connect(
        "cluster-a",
        "cluster-b",
    )

    bridge.connect(
        "cluster-b",
        "cluster-c",
    )

    connections = bridge.connections()

    assert len(connections) == 2


def test_bridge_returns_copy():

    bridge = InteroperabilityBridge()

    bridge.connect(
        "cluster-a",
        "cluster-b",
    )

    first = bridge.connections()
    second = bridge.connections()

    assert first is not second

    first.clear()

    assert len(
        bridge.connections()
    ) == 1