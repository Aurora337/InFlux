from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PenaltyResult:
    """
    Represents a validator penalty outcome.
    """

    validator_id: str

    penalty: int

    active: bool


class PenaltyEngine:
    """
    Applies deterministic validator penalties.
    """

    def apply(
        self,
        validator_id: str,
        severity: int,
    ) -> PenaltyResult:
        """
        Calculate penalty from fault severity.
        """

        penalty = max(
            severity,
            0,
        )

        return PenaltyResult(
            validator_id=validator_id,
            penalty=penalty,
            active=penalty < 10,
        )