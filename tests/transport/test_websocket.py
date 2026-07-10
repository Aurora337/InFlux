import pytest

from influx.transport.websocket import (
    WebSocketEndpoint,
    WebSocketTransport,
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
        sender="node-2",
        payload={"height": 50},
    )


def test_connect():

    endpoint = WebSocketEndpoint(
        url="ws://localhost:8080",
    )

    transport = WebSocketTransport(
        endpoint,
    )

    transport.connect()

    assert transport.connected is True


def test_disconnect():

    endpoint = WebSocketEndpoint(
        url="ws://localhost:8080",
    )

    transport = WebSocketTransport(
        endpoint,
    )

    transport.connect()
    transport.disconnect()

    assert transport.connected is False


def test_send_receive():

    endpoint = WebSocketEndpoint(
        url="ws://localhost:8080",
    )

    transport = WebSocketTransport(
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


def test_connect_without_url():

    endpoint = WebSocketEndpoint(
        url="",
    )

    transport = WebSocketTransport(
        endpoint,
    )

    with pytest.raises(
        ConnectionError,
    ):
        transport.connect()


def test_send_without_connection():

    endpoint = WebSocketEndpoint(
        url="ws://localhost:8080",
    )

    transport = WebSocketTransport(
        endpoint,
    )

    with pytest.raises(
        ConnectionError,
    ):
        transport.send(
            create_message(),
        )