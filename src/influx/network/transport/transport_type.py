from __future__ import annotations

from enum import Enum


class TransportType(str, Enum):
    """
    Supported InFlux transport mechanisms.

    Transport types describe how bytes move between nodes.
    They do not contain implementation details.

    New transport implementations should extend this enum
    without changing existing values.
    """

    TCP = "TCP"

    QUIC = "QUIC"

    WEBSOCKET = "WEBSOCKET"

    LOCAL = "LOCAL"

    SIMULATION = "SIMULATION"