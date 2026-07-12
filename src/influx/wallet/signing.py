from __future__ import annotations

import base64
import hashlib
from typing import Optional

from .transactions import (
    WalletTransaction,
)


class LegacyWalletSigner:
    """Legacy deterministic SHA256-based signer kept for compatibility."""

    def sign(self, transaction: WalletTransaction, private_key: str) -> str:
        payload = transaction.transaction_id + private_key
        signature = hashlib.sha256(payload.encode()).hexdigest()
        transaction.attach_signature(signature)
        return signature

    def verify(self, transaction: WalletTransaction, private_key: str) -> bool:
        if transaction.signature is None:
            return False
        expected = hashlib.sha256((transaction.transaction_id + private_key).encode()).hexdigest()
        return transaction.signature == expected


class Ed25519WalletSigner:
    """Ed25519 signer using PyNaCl.

    Signatures are stored as `ed25519:` + base64(signature_bytes).
    Private and public keys are passed as hex-encoded strings in this API for
    testability and transportability.
    """

    def __init__(self) -> None:
        try:
            from nacl.signing import SigningKey, VerifyKey  # type: ignore
            from nacl.exceptions import BadSignatureError  # type: ignore
        except Exception as exc:  # pragma: no cover - environment
            raise RuntimeError("PyNaCl is required for Ed25519 signing") from exc

        self._SigningKey = SigningKey
        self._VerifyKey = VerifyKey
        self._BadSignatureError = BadSignatureError

    def sign(self, transaction: WalletTransaction, private_key_hex: str) -> str:
        sk_bytes = bytes.fromhex(private_key_hex)
        sk = self._SigningKey(sk_bytes)
        sig = sk.sign(transaction.transaction_id.encode()).signature
        sig_b64 = base64.b64encode(sig).decode()
        signature = f"ed25519:{sig_b64}"
        transaction.attach_signature(signature)
        return signature

    def verify(self, transaction: WalletTransaction, public_key_hex: str) -> bool:
        if transaction.signature is None:
            return False
        if not transaction.signature.startswith("ed25519:"):
            return False
        sig_b64 = transaction.signature.split(":", 1)[1]
        sig = base64.b64decode(sig_b64)
        pk_bytes = bytes.fromhex(public_key_hex)
        vk = self._VerifyKey(pk_bytes)
        try:
            vk.verify(transaction.transaction_id.encode(), sig)
            return True
        except self._BadSignatureError:
            return False


# Backwards compatible name for existing tests/code. Keep `WalletSigner` available.
WalletSigner = LegacyWalletSigner

__all__ = ["LegacyWalletSigner", "Ed25519WalletSigner", "WalletSigner"]