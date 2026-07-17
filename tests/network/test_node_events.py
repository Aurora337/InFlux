from influx.network.node.node_event import NodeEvent
from influx.network.node.node_events import NodeEvents


def create_event() -> NodeEvent:
    return NodeEvent(
        event_type="START",
        node_id="node-1",
        timestamp=123,
        details={"status": "ok"},
    )


def test_record_event() -> None:
    events = NodeEvents()

    event = create_event()

    events.record(event)

    assert events.count() == 1
    assert events.events()[0].event_type == "START"


def test_clear_events() -> None:
    events = NodeEvents()

    events.record(create_event())

    events.clear()

    assert events.count() == 0