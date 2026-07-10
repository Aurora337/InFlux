from __future__ import annotations

from dataclasses import dataclass

import hashlib


@dataclass(slots=True, frozen=True)
class WalletAddress:
    """
    Represents an InFlux wallet address.
    """

    address: str

    account_id: str

    created_at: int


class AddressManager:
    """
    Generates and validates wallet addresses.
    """

    def generate(
        self,
        account_id: str,
        public_key: str,
        created_at: int,
    ) -> WalletAddress:
        """
        Create deterministic wallet address.
        """

        payload = (
            account_id
            + public_key
            + str(created_at)
        )

        digest = hashlib.sha256(
            payload.encode()
        ).hexdigest()

        return WalletAddress(
            address=digest,
            account_id=account_id,
            created_at=created_at,
        )

    def validate(
        self,
        address: WalletAddress,
    ) -> bool:
        """
        Validate address structure.
        """

        return (
            len(address.address)
            == 64
            and bool(address.account_id)
        )