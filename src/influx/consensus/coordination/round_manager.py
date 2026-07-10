from __future__ import annotations

from typing import Dict, Optional

from .consensus_round import ConsensusRound


class RoundManager:
    """
    Manages consensus rounds.
    """


    def __init__(
        self,
    ) -> None:

        self.rounds: Dict[
            str,
            ConsensusRound,
        ] = {}


    def add(
        self,
        round_instance: ConsensusRound,
    ) -> bool:
        """
        Register round.
        """

        if round_instance.round_id in self.rounds:
            return False

        self.rounds[
            round_instance.round_id
        ] = round_instance

        return True


    def lookup(
        self,
        round_id: str,
    ) -> Optional[ConsensusRound]:
        """
        Retrieve round.
        """

        return self.rounds.get(
            round_id
        )


    def active(
        self,
    ) -> list[ConsensusRound]:
        """
        Return unfinished rounds.
        """

        return [
            round_instance
            for round_instance
            in self.rounds.values()
            if not round_instance.completed
        ]


    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic round snapshot.
        """

        return {
            round_id:
                round_instance.snapshot()

            for round_id, round_instance
            in self.rounds.items()
        }