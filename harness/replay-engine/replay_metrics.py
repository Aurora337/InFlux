"""Metrics helpers for replay determinism health calculations."""

from dataclasses import dataclass


@dataclass
class ReplayMetrics:
    successful_replays: int
    total_replays: int

    @property
    def determinism_score(self) -> float:
        if self.total_replays == 0:
            return 0.0
        return self.successful_replays / self.total_replays

    @property
    def replay_success_rate(self) -> float:
        return self.determinism_score

    def to_dict(self) -> dict:
        return {
            "successful_replays": self.successful_replays,
            "total_replays": self.total_replays,
            "replay_success_rate": self.replay_success_rate,
            "determinism_score": self.determinism_score,
        }


__all__ = ["ReplayMetrics"]
