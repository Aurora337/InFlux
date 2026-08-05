from __future__ import annotations

from dataclasses import dataclass, field

from .consensus_config import ConsensusConfig
from .consensus_result import ConsensusResult
from .consensus_state import ConsensusState


@dataclass(slots=True)
class Consensus:
    """
    Deterministic consensus session.
    """

    config: ConsensusConfig = field(
        default_factory=ConsensusConfig
    )

    state: ConsensusState = (
        ConsensusState.IDLE
    )

    result: ConsensusResult = field(
        default_factory=ConsensusResult
    )

    def propose(
        self,
    ) -> bool:
        self.state = ConsensusState.PROPOSING
        return True

    def begin_vote(
        self,
    ) -> bool:
        self.state = ConsensusState.VOTING
        return True

    def commit(
        self,
    ) -> bool:
        self.state = ConsensusState.COMMITTED
        self.result.accepted = True
        return True

    def fail(
        self,
    ) -> bool:
        self.state = ConsensusState.FAILED
        return True

    def snapshot(
        self,
    ) -> dict[str, object]:
        return {
            "state": self.state.value,
            "result": self.result.snapshot(),
        }