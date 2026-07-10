from __future__ import annotations

import hashlib

from .transactions import (
    WalletTransaction,
)


class WalletSigner:
    """
    Handles wallet transaction signing.

    Designed as an integration layer
    with the InFlux identity subsystem.
    """

    def sign(
        self,
        transaction: WalletTransaction,
        private_key: str,
    ) -> str:
        """
        Create deterministic transaction signature.
        """

        payload = (
            transaction.transaction_id
            + private_key
        )

        signature = hashlib.sha256(
            payload.encode()
        ).hexdigest()

        transaction.attach_signature(
            signature
        )

        return signature

    def verify(
        self,
        transaction: WalletTransaction,
        private_key: str,
    ) -> bool:
        """
        Verify transaction signature.
        """

        if transaction.signature is None:
            return False

        expected = hashlib.sha256(
            (
                transaction.transaction_id
                + private_key
            ).encode()
        ).hexdigest()

        return (
            transaction.signature
            == expected
        )