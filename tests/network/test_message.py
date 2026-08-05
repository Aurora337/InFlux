from influx.network.message import NetworkMessage
from influx.network.errors import MessageError

import pytest


def create_message() -> NetworkMessage:
    return NetworkMessage(
        message_id="msg-1",
        message_type="PING",
        sender_id="node-1",
        receiver_id="node-2",
        epoch=1,
        slot=1,
        timestamp=123456789,
        payload={},
    )


def test_message_validation() -> None:
    message = create_message()

    assert message.validate() is None


def test_missing_type() -> None:
    with pytest.raises(MessageError):
        NetworkMessage(
            message_id="msg-1",
            message_type="",
            sender_id="node-1",
            receiver_id="node-2",
            epoch=1,
            slot=1,
            timestamp=123456789,
            payload={},
        ).validate()


def test_missing_sender() -> None:
    with pytest.raises(MessageError):
        NetworkMessage(
            message_id="msg-1",
            message_type="PING",
            sender_id="",
            receiver_id="node-2",
            epoch=1,
            slot=1,
            timestamp=123456789,
            payload={},
        ).validate()