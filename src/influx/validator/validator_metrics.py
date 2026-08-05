from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ValidatorMetrics:
    """
    Tracks validator lifecycle activity.
    """

    validators_registered: int = 0

    activations: int = 0

    deactivations: int = 0

    schedules_created: int = 0

    rotations_created: int = 0

    def record_registration(
        self,
    ) -> None:
        """
        Record validator registration.
        """

        self.validators_registered += 1

    def record_activation(
        self,
    ) -> None:
        """
        Record validator activation.
        """

        self.activations += 1

    def record_deactivation(
        self,
    ) -> None:
        """
        Record validator deactivation.
        """

        self.deactivations += 1

    def record_schedule(
        self,
    ) -> None:
        """
        Record validator schedule.
        """

        self.schedules_created += 1

    def record_rotation(
        self,
    ) -> None:
        """
        Record rotation creation.
        """

        self.rotations_created += 1

    def snapshot(
        self,
    ) -> dict:
        """
        Return deterministic metrics snapshot.
        """

        return {
            "validators_registered":
                self.validators_registered,

            "activations":
                self.activations,

            "deactivations":
                self.deactivations,

            "schedules_created":
                self.schedules_created,

            "rotations_created":
                self.rotations_created,
        }