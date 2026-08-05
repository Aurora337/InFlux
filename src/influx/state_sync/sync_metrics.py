from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SyncMetrics:
    """
    Tracks state synchronization activity.
    """

    sync_attempts: int = 0

    successful_syncs: int = 0

    failed_syncs: int = 0

    diffs_generated: int = 0

    proofs_created: int = 0

    proofs_verified: int = 0

    def record_attempt(
        self,
    ) -> None:
        """
        Record synchronization attempt.
        """

        self.sync_attempts += 1

    def record_success(
        self,
    ) -> None:
        """
        Record successful synchronization.
        """

        self.successful_syncs += 1

    def record_failure(
        self,
    ) -> None:
        """
        Record failed synchronization.
        """

        self.failed_syncs += 1

    def record_diff(
        self,
    ) -> None:
        """
        Record generated diff.
        """

        self.diffs_generated += 1

    def record_proof(
        self,
    ) -> None:
        """
        Record proof creation.
        """

        self.proofs_created += 1

    def record_verification(
        self,
    ) -> None:
        """
        Record proof verification.
        """

        self.proofs_verified += 1

    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic metrics snapshot.
        """

        return {
            "sync_attempts":
                self.sync_attempts,

            "successful_syncs":
                self.successful_syncs,

            "failed_syncs":
                self.failed_syncs,

            "diffs_generated":
                self.diffs_generated,

            "proofs_created":
                self.proofs_created,

            "proofs_verified":
                self.proofs_verified,
        }