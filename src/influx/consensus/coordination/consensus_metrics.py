from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ConsensusMetrics:
    """
    Tracks consensus coordination activity.
    """

    proposals_created: int = 0

    proposals_accepted: int = 0

    proposals_rejected: int = 0

    votes_received: int = 0

    votes_accepted: int = 0

    rounds_completed: int = 0

    validation_failures: int = 0


    def record_proposal(
        self,
    ) -> None:

        self.proposals_created += 1


    def record_accept(
        self,
    ) -> None:

        self.proposals_accepted += 1


    def record_reject(
        self,
    ) -> None:

        self.proposals_rejected += 1


    def record_vote(
        self,
    ) -> None:

        self.votes_received += 1


    def record_vote_accept(
        self,
    ) -> None:

        self.votes_accepted += 1


    def record_round_complete(
        self,
    ) -> None:

        self.rounds_completed += 1


    def record_failure(
        self,
    ) -> None:

        self.validation_failures += 1


    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic metrics snapshot.
        """

        return {
            "proposals_created":
                self.proposals_created,

            "proposals_accepted":
                self.proposals_accepted,

            "proposals_rejected":
                self.proposals_rejected,

            "votes_received":
                self.votes_received,

            "votes_accepted":
                self.votes_accepted,

            "rounds_completed":
                self.rounds_completed,

            "validation_failures":
                self.validation_failures,
        }