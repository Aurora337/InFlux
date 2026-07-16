from influx.network.errors import MessageError
from influx.network.message import NetworkMessage

import pytest


def test_message_validation() -> None:
    message = NetworkMessage(
        message_type="PING",
        sender="node-1",
    )

    message.validate()


def test_missing_type() -> None:
    with pytest.raises(MessageError):
        NetworkMessage(
            message_type="",
            sender="node-1",
        ).validate()


def test_missing_sender() -> None:
    with pytest.raises(MessageError):
        NetworkMessage(
            message_type="PING",
            sender="",
        ).validate()