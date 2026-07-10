from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class WalletAccount:
    """
    Represents a deterministic InFlux wallet account.

    A wallet account is linked to an identity
    and maintains associated wallet addresses.
    """

    account_id: str

    identity_id: str

    created_at: int

    active: bool = True

    addresses: list[str] = field(
        default_factory=list
    )

    def add_address(
        self,
        address: str,
    ) -> None:
        """
        Attach an address to the account.
        """

        if address not in self.addresses:
            self.addresses.append(
                address
            )

    def remove_address(
        self,
        address: str,
    ) -> bool:
        """
        Remove an address from account.
        """

        if address in self.addresses:

            self.addresses.remove(
                address
            )

            return True

        return False

    def deactivate(
        self,
    ) -> None:
        """
        Disable wallet account.
        """

        self.active = False

    def activate(
        self,
    ) -> None:
        """
        Enable wallet account.
        """

        self.active = True

    def to_dict(
        self,
    ) -> dict[str, object]:
        """
        Serialize wallet account.
        """

        return {
            "account_id": self.account_id,
            "identity_id": self.identity_id,
            "created_at": self.created_at,
            "active": self.active,
            "addresses": list(
                self.addresses
            ),
        }