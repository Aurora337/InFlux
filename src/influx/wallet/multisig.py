from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import List

from .signing import Ed25519WalletSigner
from .transactions import WalletTransaction


@dataclass
class MultisigPolicy:
    signers: List[str]  # list of public_key_hex
    threshold: int


class MultisigSigner:
    """Collect individual Ed25519 signatures and produce a multisig blob."""

    def __init__(self) -> None:
        self._ed = Ed25519WalletSigner()

    def sign(self, transaction: WalletTransaction, private_keys_hex: List[str], public_keys_hex: List[str]) -> str:
        # create list of {signer:pub, signature:ed25519:...}
        sigs = []
        for sk_hex, pk_hex in zip(private_keys_hex, public_keys_hex):
            sig = self._ed.sign(transaction, sk_hex)
            sigs.append({"signer": pk_hex, "signature": sig})
        payload = json.dumps(sigs, sort_keys=True)
        blob = base64.b64encode(payload.encode()).decode()
        return f"multisig:{blob}"

    def verify(self, transaction: WalletTransaction, policy: MultisigPolicy) -> bool:
        if transaction.signature is None:
            return False
        if not transaction.signature.startswith("multisig:"):
            return False
        blob = transaction.signature.split(":", 1)[1]
        payload = base64.b64decode(blob).decode()
        sigs = json.loads(payload)
        # count valid signatures from allowed signers
        valid = 0
        for entry in sigs:
            signer = entry.get("signer")
            signature = entry.get("signature")
            if signer not in policy.signers:
                continue
            # create temp transaction copy with only this signature
            tmp = WalletTransaction(
                sender=transaction.sender,
                inputs=transaction.inputs,
                outputs=transaction.outputs,
                timestamp=transaction.timestamp,
            )
            tmp.attach_signature(signature)
            if self._ed.verify(tmp, signer):
                valid += 1
        return valid >= policy.threshold
