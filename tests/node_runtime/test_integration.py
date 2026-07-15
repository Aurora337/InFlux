from influx.node_runtime import (
    RuntimeNode,
    NodeConfiguration,
    NodeIdentity,
    NodeHealth,
    NodeLifecycle,
    NodeManager,
    NodeService,
    NodeShutdown,
)


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


def test_node_runtime_flow() -> None:
    node = build_node()

    lifecycle = NodeLifecycle(node)

    lifecycle.start()

    manager = NodeManager()
    manager.register(node)

    service = NodeService(
        name="runtime",
        node=node,
    )

    service.start()

    assert manager.count() == 1
    assert service.active is True

    shutdown = NodeShutdown(
        lifecycle,
    )

    shutdown.execute()

    assert shutdown.completed is True
    assert lifecycle.is_running() is False