from influx.testnet.node import TestnetNode


def test_node_creation() -> None:
    node = TestnetNode(
        node_id="node-1",
    )

    assert node.node_id == "node-1"
    assert node.online is False


def test_node_start() -> None:
    node = TestnetNode(
        node_id="node-1",
    )

    node.start()

    assert node.online is True
    assert node.status() == "online"


def test_node_stop() -> None:
    node = TestnetNode(
        node_id="node-1",
    )

    node.start()
    node.stop()

    assert node.online is False