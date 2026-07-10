from __future__ import annotations

from .proposal import Proposal
from .vote import Vote
from .proposal_state import ProposalState
from .vote_state import VoteState


class ConsensusValidator:
    """
    Validates consensus operations.
    """


    def validate_proposal(
        self,
        proposal: Proposal,
    ) -> bool:
        """
        Validate proposal structure.
        """

        if not proposal.proposal_id:
            return False


        if not proposal.proposer:
            return False


        if proposal.payload is None:
            return False


        return True


    def validate_vote(
        self,
        vote: Vote,
    ) -> bool:
        """
        Validate vote structure.
        """

        if not vote.vote_id:
            return False


        if not vote.proposal_id:
            return False


        if not vote.validator:
            return False


        return True


    def validate_transition(
        self,
        current: ProposalState,
        target: ProposalState,
    ) -> bool:
        """
        Validate proposal state transition.
        """

        allowed = {

            ProposalState.CREATED: [
                ProposalState.SUBMITTED,
            ],

            ProposalState.SUBMITTED: [
                ProposalState.VALIDATING,
            ],

            ProposalState.VALIDATING: [
                ProposalState.ACCEPTED,
                ProposalState.REJECTED,
            ],

            ProposalState.ACCEPTED: [
                ProposalState.FINALIZED,
            ],
        }


        return target in allowed.get(
            current,
            [],
        )


    def validate_vote_state(
        self,
        current: VoteState,
        target: VoteState,
    ) -> bool:
        """
        Validate vote transition.
        """

        allowed = {

            VoteState.CREATED: [
                VoteState.CAST,
            ],

            VoteState.CAST: [
                VoteState.VERIFIED,
            ],

            VoteState.VERIFIED: [
                VoteState.ACCEPTED,
                VoteState.REJECTED,
            ],
        }


        return target in allowed.get(
            current,
            [],
        )