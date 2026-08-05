from __future__ import annotations

from enum import Enum


class ConnectionState(str, Enum):
    """
    Deterministic lifecycle states for a network connection.
    """

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    CLOSING = "closing"
    CLOSED = "closed"