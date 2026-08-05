from __future__ import annotations

from typing import Dict, Optional

from .vote import Vote


class VoteManager:
    """
    Manages validator votes.
    """


    def __init__(
        self,
    ) -> None:

        self.votes: Dict[
            str,
            Vote,
        ] = {}


    def add(
        self,
        vote: Vote,
    ) -> bool:
        """
        Register vote.
        """

        if vote.vote_id in self.votes:
            return False

        self.votes[
            vote.vote_id
        ] = vote

        return True


    def lookup(
        self,
        vote_id: str,
    ) -> Optional[Vote]:
        """
        Find vote.
        """

        return self.votes.get(
            vote_id
        )


    def proposal_votes(
        self,
        proposal_id: str,
    ) -> list[Vote]:
        """
        Return votes for proposal.
        """

        return [
            vote
            for vote in self.votes.values()
            if vote.proposal_id == proposal_id
        ]


    def count_approved(
        self,
        proposal_id: str,
    ) -> int:
        """
        Count approvals.
        """

        return len(
            [
                vote
                for vote in self.proposal_votes(
                    proposal_id
                )
                if vote.approved
            ]
        )


    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic vote snapshot.
        """

        return {
            vote_id:
                vote.snapshot()

            for vote_id, vote
            in self.votes.items()
        }