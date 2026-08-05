from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ChainScore:
    """
    Represents deterministic chain ranking.
    """

    height: int

    root_hash: str


class ChainSelector:
    """
    Selects canonical chain candidate.
    """

    def select(
        self,
        chains: list[ChainScore],
    ) -> ChainScore | None:
        """
        Select deterministic canonical chain.
        """

        if not chains:
            return None

        return sorted(
            chains,
            key=lambda chain: (
                chain.height,
                chain.root_hash,
            ),
            reverse=True,
        )[0]