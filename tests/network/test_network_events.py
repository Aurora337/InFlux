from influx.network.network_events import (
    NetworkEvent,
    NetworkEventType,
)


def test_event_creation():

    event = NetworkEvent(
        NetworkEventType.PEER_CONNECTED,
        source="node-a",
    )

    assert event.event_type == NetworkEventType.PEER_CONNECTED



def test_event_snapshot():

    event = NetworkEvent(
        NetworkEventType.MESSAGE_ROUTED,
        source="node-a",
        target="node-b",
    )

    snapshot = event.snapshot()

    assert snapshot["event_type"] == "message_routed"
    assert snapshot["source"] == "node-a"
    assert snapshot["target"] == "node-b"