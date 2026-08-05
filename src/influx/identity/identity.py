from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Identity:
    """
    Represents a deterministic InFlux identity.

    An identity binds a unique identifier
    to a public cryptographic key.
    """

    identity_id: str

    public_key: str

    created_at: int

    active: bool = True

    def deactivate(
        self,
    ) -> None:
        """
        Disable the identity.
        """

        self.active = False

    def activate(
        self,
    ) -> None:
        """
        Enable the identity.
        """

        self.active = True

    def to_dict(
        self,
    ) -> dict[str, object]:
        """
        Return deterministic representation.
        """

        return {
            "identity_id": self.identity_id,
            "public_key": self.public_key,
            "created_at": self.created_at,
            "active": self.active,
        }