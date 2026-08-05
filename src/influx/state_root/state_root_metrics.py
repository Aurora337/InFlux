from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class StateRootMetrics:
    """
    Tracks state root generation
    and validation activity.
    """

    roots_generated: int = 0

    commitments_created: int = 0

    validations_performed: int = 0

    validation_failures: int = 0

    root_comparisons: int = 0

    def record_root(
        self,
    ) -> None:
        """
        Record generated state root.
        """

        self.roots_generated += 1

    def record_commitment(
        self,
    ) -> None:
        """
        Record commitment creation.
        """

        self.commitments_created += 1

    def record_validation(
        self,
        success: bool,
    ) -> None:
        """
        Record validation attempt.
        """

        self.validations_performed += 1

        if not success:
            self.validation_failures += 1

    def record_comparison(
        self,
    ) -> None:
        """
        Record root comparison.
        """

        self.root_comparisons += 1

    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic metrics snapshot.
        """

        return {
            "roots_generated":
                self.roots_generated,

            "commitments_created":
                self.commitments_created,

            "validations_performed":
                self.validations_performed,

            "validation_failures":
                self.validation_failures,

            "root_comparisons":
                self.root_comparisons,
        }