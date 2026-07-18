from __future__ import annotations

from dataclasses import dataclass, field

from .consensus_vote import ConsensusVote


@dataclass(slots=True)
class ConsensusRound:
    """
    Deterministic voting round.
    """

    round_number: int = 1

    votes: list[ConsensusVote] = field(
        default_factory=list
    )

    def add_vote(
        self,
        vote: ConsensusVote,
    ) -> bool:
        """
        Add a vote if the voter has not already voted.
        """

        for existing in self.votes:
            if existing.voter == vote.voter:
                return False

        self.votes.append(vote)
        return True

    def approvals(
        self,
    ) -> int:
        """
        Count approval votes.
        """

        return sum(
            vote.weight
            for vote in self.votes
            if vote.approve
        )

    def rejections(
        self,
    ) -> int:
        """
        Count rejection votes.
        """

        return sum(
            vote.weight
            for vote in self.votes
            if not vote.approve
        )

    def snapshot(
        self,
    ) -> dict[str, int]:
        """
        Return deterministic snapshot.
        """

        return {
            "round_number": self.round_number,
            "votes": len(self.votes),
            "approvals": self.approvals(),
            "rejections": self.rejections(),
        }