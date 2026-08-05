from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SnapshotMetrics:
    """
    Tracks snapshot and recovery activity.
    """

    snapshots_created: int = 0

    checkpoints_created: int = 0

    snapshots_loaded: int = 0

    bootstrap_attempts: int = 0

    bootstrap_successes: int = 0

    bootstrap_failures: int = 0

    def record_snapshot(
        self,
    ) -> None:
        """
        Record snapshot creation.
        """

        self.snapshots_created += 1

    def record_checkpoint(
        self,
    ) -> None:
        """
        Record checkpoint creation.
        """

        self.checkpoints_created += 1

    def record_load(
        self,
    ) -> None:
        """
        Record snapshot loading.
        """

        self.snapshots_loaded += 1

    def record_bootstrap(
        self,
        success: bool,
    ) -> None:
        """
        Record bootstrap attempt.
        """

        self.bootstrap_attempts += 1

        if success:
            self.bootstrap_successes += 1
        else:
            self.bootstrap_failures += 1

    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic metrics snapshot.
        """

        return {
            "snapshots_created":
                self.snapshots_created,

            "checkpoints_created":
                self.checkpoints_created,

            "snapshots_loaded":
                self.snapshots_loaded,

            "bootstrap_attempts":
                self.bootstrap_attempts,

            "bootstrap_successes":
                self.bootstrap_successes,

            "bootstrap_failures":
                self.bootstrap_failures,
        }