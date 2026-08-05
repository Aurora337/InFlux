from __future__ import annotations

from dataclasses import dataclass

from .protocol import TransportMessage
from .exceptions import ConnectionError


@dataclass(slots=True)
class TCPEndpoint:
    """
    Represents a TCP network endpoint.
    """

    host: str

    port: int


class TCPTransport:
    """
    TCP transport abstraction.

    Provides a deterministic interface for
    sending and receiving protocol messages.
    """

    def __init__(
        self,
        endpoint: TCPEndpoint,
    ) -> None:

        self.endpoint = endpoint
        self.connected = False

    def connect(
        self,
    ) -> None:
        """
        Establish TCP connection.

        Placeholder abstraction for future
        socket implementation.
        """

        if not self.endpoint.host:

            raise ConnectionError(
                "missing host"
            )

        self.connected = True

    def disconnect(
        self,
    ) -> None:
        """
        Close TCP connection.
        """

        self.connected = False

    def send(
        self,
        message: TransportMessage,
    ) -> bytes:
        """
        Serialize outgoing message.
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