from __future__ import annotations

from dataclasses import dataclass

from .protocol import TransportMessage
from .exceptions import ConnectionError


@dataclass(slots=True)
class WebSocketEndpoint:
    """
    Represents a WebSocket endpoint.
    """

    url: str


class WebSocketTransport:
    """
    WebSocket transport abstraction.

    Provides a message interface that can
    later connect to async websocket servers.
    """

    def __init__(
        self,
        endpoint: WebSocketEndpoint,
    ) -> None:

        self.endpoint = endpoint
        self.connected = False

    def connect(
        self,
    ) -> None:
        """
        Establish WebSocket connection.
        """

        if not self.endpoint.url:

            raise ConnectionError(
                "missing websocket url"
            )

        self.connected = True

    def disconnect(
        self,
    ) -> None:
        """
        Close WebSocket connection.
        """

        self.connected = False

    def send(
        self,
        message: TransportMessage,
    ) -> bytes:
        """
        Prepare outgoing message.
        """

        if not self.connected:

            raise ConnectionError(
                "not connected"
            )

        return message.serialize()

    def receive(
        self,
        data: bytes,
    ) -> TransportMessage:
        """
        Decode incoming message.
        """

        if not self.connected:

            raise ConnectionError(
                "not connected"
            )

        return TransportMessage.deserialize(
            data
        )