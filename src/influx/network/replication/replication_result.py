from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ReplicationResult:
    """
    Result of a replication operation.
    """

    success: bool

    replicas_written: int = 0

    error: str | None = None

    def snapshot(
        self,
    ) -> dict[str, bool | int | str | None]:
        """
        Return deterministic result snapshot.
        """

        return {
            "success": self.success,
            "replicas_written": self.replicas_written,
            "error": self.error,
        }