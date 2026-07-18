from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ConsensusMetrics:
    """
    Tracks consensus statistics.
    """

    rounds_started: int = 0

    rounds_committed: int = 0

    rounds_failed: int = 0

    votes_cast: int = 0

    def snapshot(
        self,
    ) -> dict[str, int]:
        """
        Return deterministic metrics snapshot.
        """

        return {
            "rounds_started": self.rounds_started,
            "rounds_committed": self.rounds_committed,
            "rounds_failed": self.rounds_failed,
            "votes_cast": self.votes_cast,
        }