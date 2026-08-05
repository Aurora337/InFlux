from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from uuid import uuid4


@dataclass(slots=True)
class NodeIdentity:
    """
    Unique identity of an InFlux network node.

    Identity is separate from networking addresses.
    A node may change transports or locations while
    maintaining the same logical identity.
    """

    node_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    public_key: str = ""

    role: str = "validator"

    created_at: float = field(
        default_factory=time
    )

    metadata: dict = field(
        default_factory=dict
    )


    def set_metadata(
        self,
        key: str,
        value,
    ) -> None:
        """
        Store identity metadata.
        """

        self.metadata[key] = value


    def snapshot(self) -> dict:
        """
        Deterministic identity snapshot.
        """

        return {
            "node_id": self.node_id,
            "public_key": self.public_key,
            "role": self.role,
            "created_at": self.created_at,
            "metadata": dict(self.metadata),
        }