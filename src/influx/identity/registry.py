from __future__ import annotations

from .identity import Identity


class IdentityRegistry:
    """
    Stores and retrieves network identities.
    """

    def __init__(
        self,
    ) -> None:

        self._identities: dict[str, Identity] = {}

    def register(
        self,
        identity: Identity,
    ) -> None:
        """
        Register identity.
        """

        self._identities[
            identity.identity_id
        ] = identity

    def get(
        self,
        identity_id: str,
    ) -> Identity | None:
        """
        Retrieve identity.
        """

        return self._identities.get(
            identity_id
        )

    def remove(
        self,
        identity_id: str,
    ) -> bool:
        """
        Remove identity.
        """

        if identity_id in self._identities:

            del self._identities[
                identity_id
            ]

            return True

        return False

    def count(
        self,
    ) -> int:
        """
        Return identity count.
        """

        return len(
            self._identities
        )

    def identities(
        self,
    ) -> list[Identity]:
        """
        Return registered identities.
        """

        return list(
            self._identities.values()
        )