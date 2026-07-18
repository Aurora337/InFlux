from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ConsensusResult:
    """
    Result of a consensus operation.
    """

    accepted: bool = False

    round_number: int = 0

    votes: int = 0

    def snapshot(
        self,
    ) -> dict[str, bool | int]:
        return {
            "accepted": self.accepted,
            "round_number": self.round_number,
            "votes": self.votes,
        }