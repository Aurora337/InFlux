from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ClusterRecovery:
    """
    Tracks deterministic recovery operations.
    """

    recoveries: int = 0

    recovered: bool = False

    def complete(self) -> None:
        self.recoveries += 1
        self.recovered = True

    def reset(self) -> None:
        self.recovered = False

    def snapshot(
        self,
    ) -> dict[str, int | bool]:
        return {
            "recoveries": self.recoveries,
            "recovered": self.recovered,
        }