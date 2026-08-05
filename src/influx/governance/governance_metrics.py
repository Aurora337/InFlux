from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class GovernanceMetrics:
    """
    Tracks governance activity.
    """

    proposals_created: int = 0

    votes_cast: int = 0

    proposals_approved: int = 0

    proposals_rejected: int = 0

    upgrades_activated: int = 0

    def record_proposal(
        self,
    ) -> None:
        """
        Record proposal creation.
        """

        self.proposals_created += 1

    def record_vote(
        self,
    ) -> None:
        """
        Record governance vote.
        """

        self.votes_cast += 1

    def record_approval(
        self,
    ) -> None:
        """
        Record approved proposal.
        """

        self.proposals_approved += 1

    def record_rejection(
        self,
    ) -> None:
        """
        Record rejected proposal.
        """

        self.proposals_rejected += 1

    def record_upgrade(
        self,
    ) -> None:
        """
        Record activated upgrade.
        """

        self.upgrades_activated += 1

    def snapshot(
        self,
    ) -> dict:
        """
        Return deterministic governance metrics.
        """

        return {
            "proposals_created":
                self.proposals_created,

            "votes_cast":
                self.votes_cast,

            "proposals_approved":
                self.proposals_approved,

            "proposals_rejected":
                self.proposals_rejected,

            "upgrades_activated":
                self.upgrades_activated,
        }