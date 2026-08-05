from influx.network.node.network_node import NetworkNode
from influx.network.node.node_config import NodeConfig
from influx.network.node.node_coordinator import NodeCoordinator
from influx.network.node.node_event import NodeEvent
from influx.network.node.node_events import NodeEvents
from influx.network.node.node_sync import NodeSync
from influx.network.node.node_validator import NodeValidator


def create_node() -> NetworkNode:
    return NetworkNode(
        node_id="node-1",
        config=NodeConfig(),
    )


def create_coordinator() -> NodeCoordinator:
    return NodeCoordinator(
        validator=NodeValidator(),
        events=NodeEvents(),
        sync=NodeSync(),
    )


def test_node_start() -> None:
    node = create_node()
    coordinator = create_coordinator()

    result = coordinator.start(
        node,
        timestamp=100,
    )

    assert result is True
    assert node.is_running()


def test_node_start_records_event() -> None:
    node = create_node()
    coordinator = create_coordinator()

    coordinator.start(
        node,
        timestamp=100,
    )

    events = coordinator.events.events()

    assert len(events) == 1
    assert events[0].event_type == "START"
    assert events[0].node_id == "node-1"


def test_node_stop() -> None:
    node = create_node()
    coordinator = create_coordinator()

    coordinator.start(
        node,
        timestamp=100,
    )

    coordinator.stop(
        node,
        timestamp=200,
    )

    assert not node.is_running()


def test_node_stop_records_event() -> None:
    node = create_node()
    coordinator = create_coordinator()

    coordinator.stop(
        node,
        timestamp=200,
    )

    events = coordinator.events.events()

    assert len(events) == 1
    assert events[0].event_type == "STOP"


def test_node_sync_start() -> None:
    coordinator = create_coordinator()

    coordinator.synchronize(
        target_height=500,
    )

    assert coordinator.sync.target_height == 500
    assert not coordinator.sync.is_synced()