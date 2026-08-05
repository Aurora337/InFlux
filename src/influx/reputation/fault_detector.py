from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FaultEvent:
    """
    Represents a validator fault.
    """

    validator_id: str

    reason: str


class FaultDetector:
    """
    Detects validator faults.
    """

    def detect(
        self,
        validator_id: str,
        failures: int,
        threshold: int = 3,
    ) -> FaultEvent | None:
        """
        Detect excessive failures.
        """

        if failures >= threshold:

            return FaultEvent(
                validator_id=validator_id,
                reason="failure_threshold",
            )

        return None