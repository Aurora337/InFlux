from influx.testnet.faults import (
    FaultInjector,
)

from influx.testnet.node import (
    TestnetNode,
)


def test_disconnect_node() -> None:
    node = TestnetNode(
        node_id="node-1",
    )

    node.start()

    injector = FaultInjector()

    injector.disconnect(node)

    assert node.online is False


def test_reconnect_node() -> None:
    node = TestnetNode(
        node_id="node-1",
    )

    injector = FaultInjector()

    injector.reconnect(node)

    assert node.online is True