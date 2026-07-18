from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ReplicationMetrics:
    """
    Tracks replication statistics.
    """

    tasks_started: int = 0

    tasks_completed: int = 0

    tasks_failed: int = 0

    replicas_written: int = 0

    def snapshot(
        self,
    ) -> dict[str, int]:
        """
        Return deterministic metrics snapshot.
        """

        return {
            "tasks_started": self.tasks_started,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "replicas_written": self.replicas_written,
        }