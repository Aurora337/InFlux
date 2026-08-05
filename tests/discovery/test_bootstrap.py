from influx.discovery.registry import (
    PeerRegistry,
)

from influx.discovery.bootstrap import (
    BootstrapNode,
    BootstrapManager,
)


def test_add_bootstrap_node():

    registry = PeerRegistry()

    manager = BootstrapManager(
        registry
    )

    node = BootstrapNode(
        node_id="bootstrap-1",
        address="127.0.0.1",
        port=9000,
    )

    manager.add_bootstrap_node(
        node
    )

    assert len(
        manager.bootstrap_nodes()
    ) == 1


def test_bootstrap_discovery():

    registry = PeerRegistry()

    manager = BootstrapManager(
        registry
    )

    manager.add_bootstrap_node(
        BootstrapNode(
            node_id="bootstrap-1",
            address="127.0.0.1",
            port=9000,
        )
    )

    peers = manager.discover()

    assert len(peers) == 1

    assert (
        peers[0].node_id
        == "bootstrap-1"
    )