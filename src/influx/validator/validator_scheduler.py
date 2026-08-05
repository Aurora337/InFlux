from __future__ import annotations

from .validator import (
    Validator,
)

from .validator_registry import (
    ValidatorRegistry,
)


class ValidatorScheduler:
    """
    Selects validators deterministically.
    """

    def __init__(
        self,
        registry: ValidatorRegistry,
    ) -> None:

        self.registry = registry

    def select(
        self,
        index: int,
    ) -> Validator | None:
        """
        Select validator by deterministic index.
        """

        validators = (
            self.registry.active_validators()
        )

        if not validators:
            return None

        return validators[
            index % len(validators)
        ]

    def schedule(
        self,
        count: int,
    ) -> list[Validator]:
        """
        Create deterministic validator schedule.
        """

        validators = (
            self.registry.active_validators()
        )

        if not validators:
            return []

        return [
            validators[
                i % len(validators)
            ]
            for i in range(count)
        ]