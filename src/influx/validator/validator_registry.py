from __future__ import annotations

from .validator import (
    Validator,
)


class ValidatorRegistry:
    """
    Maintains registered validators.
    """

    def __init__(
        self,
    ) -> None:

        self._validators: dict[
            str,
            Validator,
        ] = {}

    def register(
        self,
        validator: Validator,
    ) -> None:
        """
        Register validator.
        """

        self._validators[
            validator.validator_id
        ] = validator

    def get(
        self,
        validator_id: str,
    ) -> Validator | None:
        """
        Retrieve validator.
        """

        return self._validators.get(
            validator_id
        )

    def active_validators(
        self,
    ) -> list[Validator]:
        """
        Return eligible validators.
        """

        return sorted(
            [
                validator
                for validator in self._validators.values()
                if validator.eligible()
            ],
            key=lambda validator:
                validator.validator_id,
        )

    def count(
        self,
    ) -> int:
        """
        Return validator count.
        """

        return len(
            self._validators
        )