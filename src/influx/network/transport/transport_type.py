from __future__ import annotations

from enum import Enum


class TransportType(str, Enum):
    """
    Supported deterministic network transports.
    """

    TCP = "tcp"
    QUIC = "quic"
    MEMORY = "memory"
    LOCAL = "local"