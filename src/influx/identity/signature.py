from __future__ import annotations

from dataclasses import dataclass

import hashlib


@dataclass(slots=True)
class Signature:
    """
    Represents a deterministic identity signature.
    """

    signer_id: str

    message_hash: str

    signature_value: str


class SignatureManager:
    """
    Handles signing and verification operations.

    This implementation provides the deterministic
    protocol abstraction. A production cryptographic
    backend can later replace the hashing mechanism.
    """

    def sign(
        self,
        identity_id: str,
        message: str,
        private_key: str,
    ) -> Signature:
        """
        Create deterministic signature.
        """

        message_hash = hashlib.sha256(
            message.encode()
        ).hexdigest()

        signature_value = hashlib.sha256(
            (
                identity_id
                + message_hash
                + private_key
            ).encode()
        ).hexdigest()

        return Signature(
            signer_id=identity_id,
            message_hash=message_hash,
            signature_value=signature_value,
        )

    def verify(
        self,
        signature: Signature,
        message: str,
        public_key: str,
    ) -> bool:
        """
        Verify signature validity.

        In production this will map to
        the selected cryptographic primitive.
        """

        message_hash = hashlib.sha256(
            message.encode()
        ).hexdigest()

        expected = hashlib.sha256(
            (
                signature.signer_id
                + message_hash
                + public_key
            ).encode()
        ).hexdigest()

        return (
            expected
            == signature.signature_value
        )