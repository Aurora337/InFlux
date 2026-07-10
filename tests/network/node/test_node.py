from influx.network.node.node import Node
from influx.network.node.node_config import NodeConfig
from influx.network.node.node_identity import NodeIdentity
from influx.network.node.node_state import NodeState


def test_node_defaults():

    node = Node()

    assert node.identity is not None
    assert node.config is not None
    assert node.state == NodeState.CREATED


def test_node_start():

    node = Node()

    node.start()

    assert node.state == NodeState.STARTING


def test_node_sync():

    node = Node()

    node.start()

    node.sync()

    assert node.state == NodeState.SYNCING


def test_node_activate():

    node = Node()

    node.start()

    node.activate()

    assert node.state == NodeState.ACTIVE
    assert node.is_healthy()


def test_node_stop():

    node = Node()

    node.start()

    node.stop()

    assert node.state == NodeState.STOPPED


def test_attach_network_components():

    node = Node()

    connection = object()
    router = object()
    transport = object()

    node.attach_network_components(
        connections=connection,
        router=router,
        transport=transport,
    )

    assert node.connections is connection
    assert node.router is router
    assert node.transport is transport


def test_custom_identity():

    identity = NodeIdentity(
        node_id="node-1",
    )

    node = Node(
        identity=identity,
    )

    assert node.identity.node_id == "node-1"


def test_custom_config():

    config = NodeConfig(
        node_name="custom",
    )

    node = Node(
        config=config,
    )

    assert node.config.node_name == "custom"


def test_snapshot():

    node = Node()

    snapshot = node.snapshot()

    assert "identity" in snapshot
    assert "health" in snapshot
    assert "metrics" in snapshot