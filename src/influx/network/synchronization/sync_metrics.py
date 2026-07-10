from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SyncMetrics:
    """
    Metrics for synchronization activity.
    """

    requests_received: int = 0

    requests_completed: int = 0

    responses_sent: int = 0

    responses_received: int = 0

    validation_failures: int = 0

    failed_syncs: int = 0


    def record_request(
        self,
    ) -> None:

        self.requests_received += 1


    def record_request_complete(
        self,
    ) -> None:

        self.requests_completed += 1


    def record_response_sent(
        self,
    ) -> None:

        self.responses_sent += 1


    def record_response_received(
        self,
    ) -> None:

        self.responses_received += 1


    def record_validation_failure(
        self,
    ) -> None:

        self.validation_failures += 1


    def record_failure(
        self,
    ) -> None:

        self.failed_syncs += 1


    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic metrics snapshot.
        """

        return {
            "requests_received":
                self.requests_received,

            "requests_completed":
                self.requests_completed,

            "responses_sent":
                self.responses_sent,

            "responses_received":
                self.responses_received,

            "validation_failures":
                self.validation_failures,

            "failed_syncs":
                self.failed_syncs,
        }