from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from uuid import uuid4
from typing import Any


@dataclass(slots=True)
class SyncResponse:
    """
    Response containing synchronization data.

    Used when a node replies to a sync request.
    """

    responder: str

    requester: str

    payload: dict[str, Any]

    response_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    timestamp: float = field(
        default_factory=time
    )

    state_hash: str = ""

    accepted: bool = True

    signature: str = ""


    def snapshot(self) -> dict[str, Any]:
        """
        Deterministic response snapshot.
        """

        return {
            "response_id":
                self.response_id,

            "responder":
                self.responder,

            "requester":
                self.requester,

            "payload":
                dict(self.payload),

            "timestamp":
                self.timestamp,

            "state_hash":
                self.state_hash,

            "accepted":
                self.accepted,

            "signature":
                self.signature,
        }