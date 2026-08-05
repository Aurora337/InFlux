"""Block data structure for deterministic state transition chain."""

from dataclasses import dataclass
from time import time


@dataclass(frozen=True)
class Block:
    height: int
    previous_hash: str
    state_hash: str
    timestamp: float

    def to_dict(self) -> dict:
        return {
            "height": self.height,
            "previous_hash": self.previous_hash,
            "state_hash": self.state_hash,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Block":
        return cls(
            height=data["height"],
            previous_hash=data["previous_hash"],
            state_hash=data["state_hash"],
            timestamp=data["timestamp"],
        )

    @classmethod
    def genesis(cls, state_hash: str) -> "Block":
        """Create the first block in the chain."""
        return cls(
            height=0,
            previous_hash="0" * 64,
            state_hash=state_hash,
            timestamp=time(),
        )


__all__ = ["Block"]
