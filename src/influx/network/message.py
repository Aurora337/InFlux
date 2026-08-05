from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .errors import MessageError


@dataclass(slots=True)
class NetworkMessage:
    """
    Deterministic protocol message.
    """

    message_id: str
    message_type: str

    sender_id: str
    receiver_id: str

    epoch: int
    slot: int

    timestamp: int

    payload: dict[str, Any]

    state_hash: str = ""
    signature: str = ""

    def validate(self) -> None:
        if not self.message_id:
            raise MessageError("missing message id")

        if not self.message_type:
            raise MessageError("missing message type")

        if not self.sender_id:
            raise MessageError("missing sender id")

        if not self.receiver_id:
            raise MessageError("missing receiver id")

        if self.epoch < 0:
            raise MessageError("invalid epoch")

        if self.slot < 0:
            raise MessageError("invalid slot")

        if self.timestamp < 0:
            raise MessageError("invalid timestamp")