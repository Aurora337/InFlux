from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ClusterMetrics:
    """
    Tracks cluster activity.
    """

    joins: int = 0

    leaves: int = 0

    elections: int = 0

    failures: int = 0


    def record_join(
        self,
    ) -> None:

        self.joins += 1


    def record_leave(
        self,
    ) -> None:

        self.leaves += 1


    def record_election(
        self,
    ) -> None:

        self.elections += 1


    def record_failure(
        self,
    ) -> None:

        self.failures += 1


    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic metrics snapshot.
        """

        return {
            "joins":
                self.joins,

            "leaves":
                self.leaves,

            "elections":
                self.elections,

            "failures":
                self.failures,
        }