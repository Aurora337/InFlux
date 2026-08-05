from __future__ import annotations

from dataclasses import dataclass

from .validator import (
    Validator,
)


@dataclass(slots=True)
class RotationRound:
    """
    Represents a validator rotation round.
    """

    round_id: int

    validators: list[Validator]


class ValidatorRotation:
    """
    Maintains validator rotation cycles.
    """

    def __init__(
        self,
    ) -> None:

        self._rounds: dict[
            int,
            RotationRound,
        ] = {}

    def create_round(
        self,
        round_id: int,
        validators: list[Validator],
    ) -> RotationRound:
        """
        Create rotation round.
        """

        rotation = RotationRound(
            round_id=round_id,
            validators=list(validators),
        )

        self._rounds[
            round_id
        ] = rotation

        return rotation

    def get_round(
        self,
        round_id: int,
    ) -> RotationRound | None:
        """
        Retrieve rotation round.
        """

        return self._rounds.get(
            round_id
        )

    def rounds(
        self,
    ) -> list[int]:
        """
        Return ordered rounds.
        """

        return sorted(
            self._rounds.keys()
        )