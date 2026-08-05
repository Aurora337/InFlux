from influx.network.node.node import Node
from influx.network.node.node_manager import NodeManager


def test_add_node():

    manager = NodeManager()

    node = Node()

    manager.add(node)

    assert (
        manager.lookup(
            node.identity.node_id
        )
        is node
    )


def test_remove_node():

    manager = NodeManager()

    node = Node()

    manager.add(node)

    manager.remove(
        node.identity.node_id
    )

    assert (
        manager.lookup(
            node.identity.node_id
        )
        is None
    )


def test_start_all():

    manager = NodeManager()

    node = Node()

    manager.add(node)

    manager.start_all()

    assert node.state.value == "starting"


def test_stop_all():

    manager = NodeManager()

    node = Node()

    manager.add(node)

    manager.start_all()

    manager.stop_all()

    assert node.state.value == "stopped"


def test_active_nodes():

    manager = NodeManager()

    node = Node()

    manager.add(node)

    node.start()

    node.activate()

    active = manager.active_nodes()

    assert node in active


def test_snapshot():

    manager = NodeManager()

    node = Node()

    manager.add(node)

    snapshot = manager.snapshot()

    assert node.identity.node_id in snapshot