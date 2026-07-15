from influx.node_runtime.configuration import NodeConfiguration
from influx.node_runtime.health import NodeHealth
from influx.node_runtime.identity import NodeIdentity
from influx.node_runtime.node import RuntimeNode


def build_node() -> RuntimeNode:
    return RuntimeNode(
        configuration=NodeConfiguration(
            node_id="node-1",
            network="testnet",
        ),
        identity=NodeIdentity(
            node_id="node-1",
            public_key="key",
        ),
        health=NodeHealth(),
    )


def test_node_start() -> None:
    node = build_node()

    node.start()

    assert node.health.online is True


def test_node_stop() -> None:
    node = build_node()

    node.start()
    node.stop()

    assert node.health.online is False


def test_node_ready() -> None:
    node = build_node()

    node.start()
    node.health.mark_synced()

    assert node.is_ready() is True