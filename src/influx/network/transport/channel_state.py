from __future__ import annotations

from enum import Enum


class ChannelState(str, Enum):
    """
    Deterministic lifecycle states for a transport channel.
    """

    CLOSED = "closed"
    OPENING = "opening"
    OPEN = "open"
    PAUSED = "paused"
    CLOSING = "closing"