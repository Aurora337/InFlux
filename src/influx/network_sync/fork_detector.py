from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ForkCandidate:
    """
    Represents a competing chain candidate.
    """

    height: int

    root_hash: str


class ForkDetector:
    """
    Detects competing historical states.
    """

    def compare(
        self,
        local: ForkCandidate,
        remote: ForkCandidate,
    ) -> bool:
        """
        Determine whether two candidates conflict.
        """

        return (
            local.height == remote.height
            and
            local.root_hash != remote.root_hash
        )

    def detect(
        self,
        candidates: list[ForkCandidate],
    ) -> list[ForkCandidate]:
        """
        Return conflicting candidates.
        """

        conflicts: list[ForkCandidate] = []

        if not candidates:
            return conflicts

        reference = candidates[0]

        for candidate in candidates[1:]:

            if self.compare(
                reference,
                candidate,
            ):
                conflicts.append(
                    candidate
                )

        return conflicts