from __future__ import annotations

from .state_diff import (
    StateDiff,
)

from .state_proof import (
    StateProof,
)


class SyncProtocol:
    """
    Handles deterministic state synchronization.
    """

    def create_package(
        self,
        previous_root: str,
        new_root: str,
        diff: StateDiff,
    ) -> dict:
        """
        Create synchronization package.
        """

        proof = StateProof.create(
            previous_root,
            new_root,
            diff,
        )

        return {
            "diff": diff,
            "proof": proof,
        }

    def validate_package(
        self,
        package: dict,
    ) -> bool:
        """
        Validate synchronization package.
        """

        diff = package["diff"]

        proof = package["proof"]

        return proof.verify_diff(
            diff
        )