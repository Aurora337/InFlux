from __future__ import annotations

from .state_commitment import (
    StateCommitment,
)


class RootValidator:
    """
    Validates state roots between nodes.
    """

    def validate(
        self,
        commitment: StateCommitment,
        state: dict[str, object],
    ) -> bool:
        """
        Validate state against commitment.
        """

        return commitment.verify(
            state
        )

    def compare(
        self,
        first: StateCommitment,
        second: StateCommitment,
    ) -> bool:
        """
        Compare two commitments.
        """

        return (
            first.height
            ==
            second.height
            and
            first.root_hash
            ==
            second.root_hash
        )

    def snapshot(
        self,
    ) -> dict:
        """
        Validator snapshot.
        """

        return {
            "component":
                "root_validator",

            "status":
                "active",
        }