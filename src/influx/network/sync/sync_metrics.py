from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SyncMetrics:
    """
    Synchronization metrics.
    """

    snapshots: int = 0

    messages: int = 0

    failures: int = 0

    def record_snapshot(self) -> None:
        self.snapshots += 1

    def record_message(self) -> None:
        self.messages += 1

    def record_failure(self) -> None:
        self.failures += 1

    def snapshot(self) -> dict[str, int]:
        return {
            "snapshots": self.snapshots,
            "messages": self.messages,
            "failures": self.failures,
        }