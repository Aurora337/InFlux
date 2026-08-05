from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Validator:
    """
    Represents a network validator.
    """

    validator_id: str

    stake: int

    active: bool = True

    def activate(
        self,
    ) -> None:
        """
        Activate validator.
        """

        self.active = True

    def deactivate(
        self,
    ) -> None:
        """
        Deactivate validator.
        """

        self.active = False

    def eligible(
        self,
    ) -> bool:
        """
        Determine validator eligibility.
        """

        return (
            self.active
            and self.stake > 0
        )