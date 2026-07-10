from __future__ import annotations

import hashlib


class MerkleTree:
    """
    Deterministic Merkle tree implementation.
    """

    def __init__(
        self,
        leaves: list[str],
    ) -> None:

        self.leaves = list(
            leaves
        )

    @staticmethod
    def hash_value(
        value: str,
    ) -> str:
        """
        Deterministic SHA-256 hash.
        """

        return hashlib.sha256(
            value.encode()
        ).hexdigest()

    def build_root(
        self,
    ) -> str:
        """
        Construct deterministic Merkle root.
        """

        if not self.leaves:
            return self.hash_value(
                ""
            )

        nodes = [
            self.hash_value(
                leaf
            )
            for leaf in self.leaves
        ]

        while len(nodes) > 1:

            if len(nodes) % 2 != 0:
                nodes.append(
                    nodes[-1]
                )

            next_level = []

            for index in range(
                0,
                len(nodes),
                2,
            ):

                combined = (
                    nodes[index]
                    +
                    nodes[index + 1]
                )

                next_level.append(
                    self.hash_value(
                        combined
                    )
                )

            nodes = next_level

        return nodes[0]

    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic tree snapshot.
        """

        return {
            "leaves":
                list(self.leaves),

            "root":
                self.build_root(),
        }