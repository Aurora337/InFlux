from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class KeyPair:
    """
    Represents a cryptographic key pair.

    This abstraction intentionally avoids
    binding the protocol to one cryptographic
    backend.
    """

    public_key: str

    private_key: str


class KeyManager:
    """
    Manages identity key lifecycle operations.
    """

    def __init__(
        self,
    ) -> None:

        self._keys: dict[str, KeyPair] = {}

    def register(
        self,
        identity_id: str,
        key_pair: KeyPair,
    ) -> None:
        """
        Register key material for identity.
        """

        self._keys[identity_id] = key_pair

    def get(
        self,
        identity_id: str,
    ) -> KeyPair | None:
        """
        Retrieve key pair.
        """

        return self._keys.get(
            identity_id
        )

    def remove(
        self,
        identity_id: str,
    ) -> bool:
        """
        Remove key association.
        """

        if identity_id in self._keys:

            del self._keys[identity_id]

            return True

        return False

    def exists(
        self,
        identity_id: str,
    ) -> bool:
        """
        Check key existence.
        """

        return (
            identity_id
            in self._keys
        )