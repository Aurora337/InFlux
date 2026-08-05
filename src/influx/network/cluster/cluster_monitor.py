from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ClusterMonitor:
    """
    Deterministic monitoring counters.
    """

    warnings: int = 0

    errors: int = 0

    observations: int = 0

    def observe(
        self,
    ) -> None:
        self.observations += 1

    def warning(
        self,
    ) -> None:
        self.warnings += 1

    def error(
        self,
    ) -> None:
        self.errors += 1

    def snapshot(
        self,
    ) -> dict[str, int]:
        return {
            "warnings": self.warnings,
            "errors": self.errors,
            "observations": self.observations,
        }