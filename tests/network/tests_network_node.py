from influx.network.node.network_node import NetworkNode
from influx.network.node.node_config import NodeConfig


def test_start_stop() -> None:
    node = NetworkNode(
        node_id="node-1",
        config=NodeConfig(),
    )

    assert not node.is_running()

    node.start()

    assert node.is_running()

    node.stop()

    assert not node.is_running()