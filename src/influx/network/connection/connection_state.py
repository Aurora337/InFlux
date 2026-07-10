from enum import Enum


class ConnectionState(str, Enum):
    """
    Deterministic lifecycle states for network connections.
    """

    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    SYNCING = "SYNCING"
    FAILED = "FAILED"
    CLOSED = "CLOSED"