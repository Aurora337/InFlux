from __future__ import annotations

from typing import Dict, Optional

from .proposal import Proposal


class ProposalManager:
    """
    Manages consensus proposals.
    """


    def __init__(
        self,
    ) -> None:

        self.proposals: Dict[
            str,
            Proposal,
        ] = {}


    def add(
        self,
        proposal: Proposal,
    ) -> bool:
        """
        Register proposal.
        """

        if proposal.proposal_id in self.proposals:
            return False

        self.proposals[
            proposal.proposal_id
        ] = proposal

        return True


    def lookup(
        self,
        proposal_id: str,
    ) -> Optional[Proposal]:
        """
        Retrieve proposal.
        """

        return self.proposals.get(
            proposal_id
        )


    def remove(
        self,
        proposal_id: str,
    ) -> bool:
        """
        Remove proposal.
        """

        if proposal_id not in self.proposals:
            return False

        del self.proposals[
            proposal_id
        ]

        return True


    def active(
        self,
    ) -> list[Proposal]:
        """
        Return active proposals.
        """

        return list(
            self.proposals.values()
        )


    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic proposal snapshot.
        """

        return {
            proposal_id:
                proposal.snapshot()

            for proposal_id, proposal
            in self.proposals.items()
        }