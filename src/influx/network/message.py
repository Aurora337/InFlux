from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NetworkMessage:
    """
    Deterministic network message.

    Every message exchanged between peers must use this structure.
    """

    message_id: str
    sender_id: str
    receiver_id: str

    epoch: int
    ctor_slot: int

    timestamp: float

    message_type: str

    payload: Any

    state_hash: str

    signature: str