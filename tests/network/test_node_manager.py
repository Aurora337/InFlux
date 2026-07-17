from influx.network.node.network_node import NetworkNode
from influx.network.node.node_config import NodeConfig
from influx.network.node.node_manager import NodeManager


def test_register_unregister() -> None:
    manager = NodeManager()

    node = NetworkNode(
        node_id="node-1",
        config=NodeConfig(),
    )

    manager.register(node)

    assert manager.count() == 1
    assert manager.get("node-1") is node

    manager.unregister("node-1")

    assert manager.count() == 0


def test_sorted_nodes() -> None:
    manager = NodeManager()

    manager.register(
        NetworkNode("b", NodeConfig())
    )

    manager.register(
        NetworkNode("a", NodeConfig())
    )

    nodes = manager.nodes()

    assert nodes[0].node_id == "a"
    assert nodes[1].node_id == "b"