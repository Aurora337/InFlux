from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ReplicationMetrics:
    """
    Replication subsystem metrics.
    """

    sessions_created: int = 0

    sessions_completed: int = 0

    sessions_failed: int = 0

    sessions_cancelled: int = 0

    bytes_replicated: int = 0

    state_diffs: int = 0

    verification_failures: int = 0

    average_sync_time: float = 0.0

    def record_created(self) -> None:
        self.sessions_created += 1

    def record_completed(self) -> None:
        self.sessions_completed += 1

    def record_failed(self) -> None:
        self.sessions_failed += 1

    def record_cancelled(self) -> None:
        self.sessions_cancelled += 1

    def record_bytes(
        self,
        count: int,
    ) -> None:
        self.bytes_replicated += count

    def record_diff(self) -> None:
        self.state_diffs += 1

    def record_verification_failure(self) -> None:
        self.verification_failures += 1

    def update_average_sync_time(
        self,
        seconds: float,
    ) -> None:
        if self.average_sync_time == 0.0:
            self.average_sync_time = seconds
        else:
            self.average_sync_time = (
                self.average_sync_time + seconds
            ) / 2.0

    def snapshot(self) -> dict:
        return {
            "sessions_created": self.sessions_created,
            "sessions_completed": self.sessions_completed,
            "sessions_failed": self.sessions_failed,
            "sessions_cancelled": self.sessions_cancelled,
            "bytes_replicated": self.bytes_replicated,
            "state_diffs": self.state_diffs,
            "verification_failures": self.verification_failures,
            "average_sync_time": self.average_sync_time,
        }