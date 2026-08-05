"""
InFlux Transport Layer.

Provides communication abstractions
for InFlux network nodes.

Components:

- TCP transport
- WebSocket transport
- Protocol messages
- Transport exceptions
"""

from .protocol import (
    TransportMessage,
)

from .tcp import (
    TCPEndpoint,
    TCPTransport,
)

from .websocket import (
    WebSocketEndpoint,
    WebSocketTransport,
)

from .exceptions import (
    TransportError,
    ConnectionError,
    ProtocolError,
    MessageValidationError,
)


__all__ = [
    "TransportMessage",
    "TCPEndpoint",
    "TCPTransport",
    "WebSocketEndpoint",
    "WebSocketTransport",
    "TransportError",
    "ConnectionError",
    "ProtocolError",
    "MessageValidationError",
]