from __future__ import annotations

from dataclasses import dataclass, field

from .consensus import Consensus
from .consensus_metrics import ConsensusMetrics
from .consensus_validator import ConsensusValidator


@dataclass(slots=True)
class ConsensusManager:
    """
    Coordinates deterministic consensus.
    """

    validator: ConsensusValidator = field(
        default_factory=ConsensusValidator
    )

    metrics: ConsensusMetrics = field(
        default_factory=ConsensusMetrics
    )

    def begin(
        self,
        consensus: Consensus,
    ) -> bool:
        """
        Begin a consensus round.
        """

        if not self.validator.validate(
            consensus,
        ):
            self.metrics.rounds_failed += 1
            return False

        consensus.propose()

        self.metrics.rounds_started += 1

        return True

    def commit(
        self,
        consensus: Consensus,
    ) -> bool:
        """
        Commit a consensus round.
        """

        consensus.commit()

        self.metrics.rounds_committed += 1

        return True