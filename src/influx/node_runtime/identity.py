from __future__ import annotations

from dataclasses import dataclass

from .errors import NodeIdentityError


@dataclass(slots=True)
class NodeIdentity:
    """
    Deterministic node identity.
    """

    node_id: str
    public_key: str

    def validate(self) -> None:
        """
        Validate identity.
        """

        if not self.node_id:
            raise NodeIdentityError(
                "missing node id"
            )

        if not self.public_key:
            raise NodeIdentityError(
                "missing public key"
            )