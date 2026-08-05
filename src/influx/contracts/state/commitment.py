from __future__ import annotations

import hashlib
import json

from .snapshot import StateSnapshot


class StateCommitment:
    """
    Deterministic contract state commitment generator.
    """

    @staticmethod
    def generate(
        snapshot: StateSnapshot,
    ) -> str:
        """
        Generate deterministic commitment hash.
        """

        payload = json.dumps(
            snapshot.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
        )

        return hashlib.sha256(
            payload.encode()
        ).hexdigest()

    @staticmethod
    def matches(
        snapshot: StateSnapshot,
        commitment: str,
    ) -> bool:
        """
        Verify snapshot against commitment.
        """

        return (
            StateCommitment.generate(snapshot)
            == commitment
        )