from influx.testnet.network import TestnetNetwork
from influx.testnet.node import TestnetNode


def test_add_node() -> None:
    network = TestnetNetwork()

    node = TestnetNode(
        node_id="node-1",
    )

    network.add_node(node)

    assert network.node_count() == 1


def test_online_nodes() -> None:
    network = TestnetNetwork()

    node = TestnetNode(
        node_id="node-1",
    )

    node.start()

    network.add_node(node)

    assert len(network.online_nodes()) == 1


def test_remove_node() -> None:
    network = TestnetNetwork()

    node = TestnetNode(
        node_id="node-1",
    )

    network.add_node(node)

    network.remove_node(
        "node-1",
    )

    assert network.node_count() == 0