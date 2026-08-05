from __future__ import annotations

from dataclasses import dataclass

import hashlib

from .state_diff import (
    StateDiff,
)


@dataclass(slots=True)
class StateProof:
    """
    Cryptographic proof of a state transition.
    """

    previous_root: str

    new_root: str

    diff_hash: str

    @classmethod
    def create(
        cls,
        previous_root: str,
        new_root: str,
        diff: StateDiff,
    ) -> "StateProof":
        """
        Create deterministic proof.
        """

        serialized = str(
            diff.snapshot()
        )

        diff_hash = hashlib.sha256(
            serialized.encode()
        ).hexdigest()

        return cls(
            previous_root=previous_root,
            new_root=new_root,
            diff_hash=diff_hash,
        )

    def verify_diff(
        self,
        diff: StateDiff,
    ) -> bool:
        """
        Verify diff integrity.
        """

        serialized = str(
            diff.snapshot()
        )

        calculated = hashlib.sha256(
            serialized.encode()
        ).hexdigest()

        return (
            calculated
            ==
            self.diff_hash
        )

    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic proof snapshot.
        """

        return {
            "previous_root":
                self.previous_root,

            "new_root":
                self.new_root,

            "diff_hash":
                self.diff_hash,
        }