from influx.network.routing.message import Message


def create_message():
    return Message(
        source="node-a",
        destination="node-b",
        payload={
            "event": "test",
        },
    )


def test_message_creation():
    message = create_message()

    assert message.source == "node-a"
    assert message.destination == "node-b"
    assert message.payload["event"] == "test"


def test_message_default_ttl():
    message = create_message()

    assert message.ttl > 0


def test_message_decrement_ttl():
    message = create_message()

    result = message.decrement_ttl()

    assert result
    assert message.ttl >= 0


def test_message_snapshot():
    message = create_message()

    snapshot = message.snapshot()

    assert snapshot["source"] == "node-a"
    assert snapshot["destination"] == "node-b"