from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class GuardDecision:
    """
    Represents a consensus security decision.
    """

    validator_id: str

    allowed: bool

    reason: str


class ConsensusGuard:
    """
    Protects consensus operations from unsafe actions.
    """

    def evaluate(
        self,
        validator_id: str,
        faults: int,
        threshold: int = 3,
    ) -> GuardDecision:
        """
        Evaluate validator safety.
        """

        if faults >= threshold:

            return GuardDecision(
                validator_id=validator_id,
                allowed=False,
                reason="fault_threshold_exceeded",
            )

        return GuardDecision(
            validator_id=validator_id,
            allowed=True,
            reason="validator_safe",
        )