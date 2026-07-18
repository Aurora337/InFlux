from influx.network.gossip.gossip_message import (
    GossipMessage,
)

from influx.network.gossip.gossip_validator import (
    GossipValidator,
)


def create_message() -> GossipMessage:
    return GossipMessage(
        message_id="msg-1",
        origin="node-1",
        payload={
            "data": "hello",
        },
        signature="signature-1",
    )


def test_valid_message() -> None:
    validator = GossipValidator()

    message = create_message()

    assert validator.validate(message)


def test_missing_origin_fails() -> None:
    validator = GossipValidator()

    message = create_message()
    message.origin = ""

    assert not validator.validate(message)


def test_missing_signature_fails() -> None:
    validator = GossipValidator()

    message = create_message()
    message.signature = ""

    assert not validator.validate(message)