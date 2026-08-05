from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ConsensusVote:
    """
    Vote cast during consensus.
    """

    voter: str

    approve: bool = True

    weight: int = 1

    def snapshot(
        self,
    ) -> dict[str, str | bool | int]:
        """
        Return deterministic snapshot.
        """

        return {
            "voter": self.voter,
            "approve": self.approve,
            "weight": self.weight,
        }