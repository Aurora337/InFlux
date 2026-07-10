from __future__ import annotations

from dataclasses import dataclass

from .proposal import Proposal



@dataclass(slots=True)
class ConsensusRound:
    """
    Represents a consensus execution round.
    """

    round_id: str

    proposal: Proposal

    completed: bool = False


    def start(
        self,
    ) -> None:
        """
        Begin round.
        """

        self.proposal.validate()


    def finalize(
        self,
    ) -> None:
        """
        Complete round.
        """

        self.proposal.finalize()

        self.completed = True


    def reject(
        self,
    ) -> None:
        """
        Reject round.
        """

        self.proposal.reject()

        self.completed = True


    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic round snapshot.
        """

        return {
            "round_id":
                self.round_id,

            "completed":
                self.completed,

            "proposal":
                self.proposal.snapshot(),
        }