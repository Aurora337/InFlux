from __future__ import annotations

from dataclasses import dataclass

from .consensus import Consensus


@dataclass(slots=True)
class ConsensusValidator:
    """
    Validates consensus sessions.
    """

    def validate(
        self,
        consensus: Consensus,
    ) -> bool:
        """
        Validate a consensus session.
        """

        try:
            consensus.config.validate()
        except ValueError:
            return False

        return True