from influx.network.gossip.gossip_message import (
    GossipMessage,
)


def create_message() -> GossipMessage:
    return GossipMessage(
        message_id="msg-1",
        origin="node-1",
        payload={
            "type": "transaction",
            "data": "hello",
        },
        signature="signature-1",
    )


def test_message_creation() -> None:
    message = create_message()

    assert message.message_id == "msg-1"
    assert message.origin == "node-1"
    assert message.signature == "signature-1"


def test_snapshot() -> None:
    message = create_message()

    snapshot = message.snapshot()

    assert snapshot["message_id"] == "msg-1"
    assert snapshot["origin"] == "node-1"
    assert snapshot["signature"] == "signature-1"


def test_increment_hop() -> None:
    message = create_message()

    assert message.hops == 0

    message.increment_hop()

    assert message.hops == 1


def test_ttl_expiration() -> None:
    message = create_message()

    message.ttl = 0

    assert message.expired()