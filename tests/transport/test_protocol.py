import pytest

from influx.transport.protocol import (
    TransportMessage,
)

from influx.transport.exceptions import (
    MessageValidationError,
)


def create_message():

    return TransportMessage(
        version="1.0",
        message_type="SYNC",
        sender="node-1",
        payload={
            "height": 100,
        },
    )


def test_message_creation():

    message = create_message()

    assert (
        message.version
        == "1.0"
    )

    assert (
        message.message_type
        == "SYNC"
    )

    assert (
        message.sender
        == "node-1"
    )


def test_message_validation():

    message = create_message()

    message.validate()


def test_message_serialization():

    message = create_message()

    encoded = message.serialize()

    assert isinstance(
        encoded,
        bytes,
    )


def test_message_deserialization():

    message = create_message()

    encoded = message.serialize()

    decoded = (
        TransportMessage.deserialize(
            encoded
        )
    )

    assert (
        decoded
        == message
    )


def test_invalid_message():

    message = TransportMessage(
        version="",
        message_type="SYNC",
        sender="node-1",
        payload={},
    )

    with pytest.raises(
        MessageValidationError
    ):

        message.validate()


def test_deterministic_serialization():

    first = create_message()

    second = create_message()

    assert (
        first.serialize()
        ==
        second.serialize()
    )