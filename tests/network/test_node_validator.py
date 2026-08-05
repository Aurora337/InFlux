from influx.network.node.network_node import NetworkNode
from influx.network.node.node_config import NodeConfig
from influx.network.node.node_state import NodeState
from influx.network.node.node_validator import NodeValidator


def test_valid_node() -> None:
    validator = NodeValidator()

    node = NetworkNode(
        node_id="node-1",
        config=NodeConfig(),
    )

    assert validator.validate(node)


def test_invalid_node() -> None:
    validator = NodeValidator()

    node = NetworkNode(
        node_id="",
        config=NodeConfig(),
    )

    assert not validator.validate(node)


def test_ready_node() -> None:
    validator = NodeValidator()

    node = NetworkNode(
        node_id="node-1",
        config=NodeConfig(),
    )

    node.state = NodeState.ACTIVE

    assert validator.ready(node)


def test_not_ready_node() -> None:
    validator = NodeValidator()

    node = NetworkNode(
        node_id="node-1",
        config=NodeConfig(),
    )

    assert not validator.ready(node)