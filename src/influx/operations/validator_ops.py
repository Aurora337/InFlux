from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ValidatorStatus:
    """
    Operational state of a validator.
    """

    validator_id: str
    online: bool
    participating: bool
    healthy: bool


@dataclass(slots=True)
class ValidatorOperations:
    """
    Tracks validator operational status.
    """

    validators: dict[str, ValidatorStatus]

    def __init__(self) -> None:
        self.validators = {}

    def update(
        self,
        status: ValidatorStatus,
    ) -> None:
        """
        Store or replace validator status.
        """

        self.validators[
            status.validator_id
        ] = status

    def validator_count(
        self,
    ) -> int:
        """
        Number of tracked validators.
        """

        return len(self.validators)

    def healthy_count(
        self,
    ) -> int:
        """
        Number of healthy validators.
        """

        return sum(
            1
            for validator in self.validators.values()
            if validator.healthy
        )

    def readiness(
        self,
    ) -> float:
        """
        Fraction of validators that are healthy.
        """

        total = self.validator_count()

        if total == 0:
            return 0.0

        return self.healthy_count() / total