from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class NetworkMetrics:
    """
    Tracks network synchronization activity.
    """

    forks_detected: int = 0

    forks_resolved: int = 0

    sync_requests: int = 0

    sync_successes: int = 0

    sync_failures: int = 0

    chain_selections: int = 0

    def record_fork(
        self,
    ) -> None:
        """
        Record detected fork.
        """

        self.forks_detected += 1

    def record_resolution(
        self,
    ) -> None:
        """
        Record successful fork resolution.
        """

        self.forks_resolved += 1

    def record_sync(
        self,
        success: bool,
    ) -> None:
        """
        Record synchronization attempt.
        """

        self.sync_requests += 1

        if success:
            self.sync_successes += 1
        else:
            self.sync_failures += 1

    def record_selection(
        self,
    ) -> None:
        """
        Record canonical chain selection.
        """

        self.chain_selections += 1

    def snapshot(
        self,
    ) -> dict:
        """
        Return deterministic metrics snapshot.
        """

        return {
            "forks_detected":
                self.forks_detected,

            "forks_resolved":
                self.forks_resolved,

            "sync_requests":
                self.sync_requests,

            "sync_successes":
                self.sync_successes,

            "sync_failures":
                self.sync_failures,

            "chain_selections":
                self.chain_selections,
        }