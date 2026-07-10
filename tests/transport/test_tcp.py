import pytest

from influx.transport.tcp import (
    TCPEndpoint,
    TCPTransport,
)

from influx.transport.protocol import (
    TransportMessage,
)

from influx.transport.exceptions import (
    ConnectionError,
)


def create_message() -> TransportMessage:

    return TransportMessage(
        version="1.0",
        message_type="PING",
        sender="node-1",
        payload={"height": 10},
    )


def test_connect():

    endpoint = TCPEndpoint(
        host="127.0.0.1",
        port=9000,
    )

    transport = TCPTransport(
        endpoint,
    )

    transport.connect()

    assert transport.connected is True


def test_disconnect():

    endpoint = TCPEndpoint(
        host="127.0.0.1",
        port=9000,
    )

    transport = TCPTransport(
        endpoint,
    )

    transport.connect()
    transport.disconnect()

    assert transport.connected is False


def test_send_receive():

    endpoint = TCPEndpoint(
        host="localhost",
        port=9000,
    )

    transport = TCPTransport(
        endpoint,
    )

    transport.connect()

    message = create_message()

    encoded = transport.send(
        message,
    )

    decoded = transport.receive(
        encoded,
    )

    assert decoded == message


def test_connect_without_host():

    endpoint = TCPEndpoint(
        host="",
        port=9000,
    )

    transport = TCPTransport(
        endpoint,
    )

    with pytest.raises(
        ConnectionError,
    ):
        transport.connect()


def test_send_without_connection():

    endpoint = TCPEndpoint(
        host="localhost",
        port=9000,
    )

    transport = TCPTransport(
        endpoint,
    )

    with pytest.raises(
        ConnectionError,
    ):
        transport.send(
            create_message(),
        )