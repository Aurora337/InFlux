from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ValidatorScore:
    """
    Represents validator reputation score.
    """

    validator_id: str

    score: int = 100

    successful_actions: int = 0

    failed_actions: int = 0

    def record_success(
        self,
    ) -> None:
        """
        Increase reputation after success.
        """

        self.successful_actions += 1
        self.score += 1

    def record_failure(
        self,
    ) -> None:
        """
        Decrease reputation after failure.
        """

        self.failed_actions += 1
        self.score -= 1

        if self.score < 0:
            self.score = 0

    def healthy(
        self,
    ) -> bool:
        """
        Determine if validator is healthy.
        """

        return self.score > 0