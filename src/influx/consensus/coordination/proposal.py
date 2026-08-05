from __future__ import annotations

from dataclasses import dataclass, field
from time import time

from .proposal_state import ProposalState


@dataclass(slots=True)
class Proposal:
    """
    Represents a consensus proposal.
    """

    proposal_id: str

    proposer: str

    payload: dict

    state: ProposalState = ProposalState.CREATED

    created_at: float = field(
        default_factory=time
    )


    def submit(
        self,
    ) -> None:
        """
        Submit proposal.
        """

        self.state = ProposalState.SUBMITTED


    def validate(
        self,
    ) -> None:
        """
        Move proposal into validation.
        """

        self.state = ProposalState.VALIDATING


    def accept(
        self,
    ) -> None:
        """
        Accept proposal.
        """

        self.state = ProposalState.ACCEPTED


    def reject(
        self,
    ) -> None:
        """
        Reject proposal.
        """

        self.state = ProposalState.REJECTED


    def finalize(
        self,
    ) -> None:
        """
        Finalize proposal.
        """

        self.state = ProposalState.FINALIZED


    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic proposal snapshot.
        """

        return {
            "proposal_id":
                self.proposal_id,

            "proposer":
                self.proposer,

            "payload":
                self.payload,

            "state":
                self.state.value,

            "created_at":
                self.created_at,
        }