from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .errors import MessageError


@dataclass(slots=True)
class NetworkMessage:
    """
    Deterministic network message.
    """

    message_id: str = ""
    sender_id: str = ""
    receiver_id: str = ""

    epoch: int = 0
    ctor_slot: int = 0
    timestamp: int = 0

    message_type: str = ""

    payload: dict[str, Any] = field(
        default_factory=dict
    )

    state_hash: str = ""
    signature: str = ""

    # compatibility
    sender: str | None = None

    def __post_init__(self) -> None:
        if self.sender and not self.sender_id:
            self.sender_id = self.sender

    def validate(self) -> None:

        if not self.message_type:
            raise MessageError(
                "missing message type"
            )

        if not self.sender_id:
            raise MessageError(
                "missing sender id"
            )