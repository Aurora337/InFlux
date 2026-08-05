from __future__ import annotations

from dataclasses import dataclass, field
from time import time

from .vote_state import VoteState


@dataclass(slots=True)
class Vote:
    """
    Represents a validator vote.
    """

    vote_id: str

    proposal_id: str

    validator: str

    approved: bool

    state: VoteState = VoteState.CREATED

    created_at: float = field(
        default_factory=time
    )


    def cast(
        self,
    ) -> None:
        """
        Cast vote.
        """

        self.state = VoteState.CAST


    def verify(
        self,
    ) -> None:
        """
        Verify vote.
        """

        self.state = VoteState.VERIFIED


    def accept(
        self,
    ) -> None:
        """
        Accept vote.
        """

        self.state = VoteState.ACCEPTED


    def reject(
        self,
    ) -> None:
        """
        Reject vote.
        """

        self.state = VoteState.REJECTED


    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic vote snapshot.
        """

        return {
            "vote_id":
                self.vote_id,

            "proposal_id":
                self.proposal_id,

            "validator":
                self.validator,

            "approved":
                self.approved,

            "state":
                self.state.value,

            "created_at":
                self.created_at,
        }