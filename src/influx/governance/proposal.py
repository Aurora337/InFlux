from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Proposal:
    """
    Represents a governance proposal.
    """

    proposal_id: str

    title: str

    description: str

    proposer: str

    votes_for: set[str] = field(
        default_factory=set
    )

    votes_against: set[str] = field(
        default_factory=set
    )

    active: bool = True

    def approve(
        self,
        validator_id: str,
    ) -> None:
        """
        Record approval vote.
        """

        self.votes_for.add(
            validator_id
        )

        self.votes_against.discard(
            validator_id
        )

    def reject(
        self,
        validator_id: str,
    ) -> None:
        """
        Record rejection vote.
        """

        self.votes_against.add(
            validator_id
        )

        self.votes_for.discard(
            validator_id
        )

    def approved(
        self,
        threshold: int = 1,
    ) -> bool:
        """
        Determine proposal approval.
        """

        return (
            len(self.votes_for)
            >= threshold
        )