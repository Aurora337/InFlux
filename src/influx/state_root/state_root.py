from __future__ import annotations

from .merkle_tree import (
    MerkleTree,
)


class StateRoot:
    """
    Generates deterministic state commitments.
    """

    def __init__(
        self,
        state: dict[str, object],
    ) -> None:

        self.state = dict(
            state
        )

    def canonical_leaves(
        self,
    ) -> list[str]:
        """
        Create deterministic state leaves.
        """

        leaves = []

        for key in sorted(
            self.state.keys()
        ):

            leaves.append(
                f"{key}:{self.state[key]}"
            )

        return leaves

    def calculate(
        self,
    ) -> str:
        """
        Calculate state root.
        """

        tree = MerkleTree(
            self.canonical_leaves()
        )

        return tree.build_root()

    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic state root snapshot.
        """

        return {
            "state":
                dict(self.state),

            "root":
                self.calculate(),
        }