from __future__ import annotations

from enum import Enum


class GossipState(str, Enum):
    """
    Deterministic gossip lifecycle states.
    """

    INITIALIZING = "initializing"

    ACTIVE = "active"

    PROPAGATING = "propagating"

    STOPPED = "stopped"