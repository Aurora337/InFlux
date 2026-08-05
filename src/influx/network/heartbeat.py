from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Heartbeat:
    """
    Simple deterministic heartbeat.
    """

    node_id: str

    epoch: int

    ctor_slot: int

    state_hash: str