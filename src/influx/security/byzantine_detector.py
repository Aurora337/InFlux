from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ByzantineEvent:
    """
    Represents detected Byzantine behavior.
    """

    validator_id: str

    reason: str

    severity: int


class ByzantineDetector:
    """
    Detects deterministic Byzantine behavior patterns.
    """

    def detect(
        self,
        validator_id: str,
        conflicting_votes: int,
        threshold: int = 2,
    ) -> ByzantineEvent | None:
        """
        Detect conflicting consensus behavior.
        """

        if conflicting_votes >= threshold:
            return ByzantineEvent(
                validator_id=validator_id,
                reason="conflicting_votes",
                severity=conflicting_votes,
            )

        return None