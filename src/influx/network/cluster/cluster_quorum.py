from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ClusterQuorum:
    """
    Determines deterministic quorum status.
    """

    required: int = 1

    present: int = 0

    def reached(self) -> bool:
        """
        Return True when quorum is satisfied.
        """

        return self.present >= self.required

    def snapshot(
        self,
    ) -> dict[str, int | bool]:
        return {
            "required": self.required,
            "present": self.present,
            "reached": self.reached(),
        }