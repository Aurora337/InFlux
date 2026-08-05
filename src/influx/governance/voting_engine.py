from __future__ import annotations

from dataclasses import dataclass

from .proposal import Proposal


@dataclass(slots=True)
class VoteResult:
    """
    Represents governance vote outcome.
    """

    proposal_id: str

    approved: bool

    votes_for: int

    votes_against: int


class VotingEngine:
    """
    Executes deterministic governance voting.
    """

    def vote(
        self,
        proposal: Proposal,
        threshold: int = 1,
    ) -> VoteResult:
        """
        Evaluate proposal result.
        """

        approved = proposal.approved(
            threshold
        )

        return VoteResult(
            proposal_id=proposal.proposal_id,
            approved=approved,
            votes_for=len(
                proposal.votes_for
            ),
            votes_against=len(
                proposal.votes_against
            ),
        )