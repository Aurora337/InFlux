from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class BlockHeader:
    """
    Identifies a deterministic block.
    """

    height: int

    previous_hash: str

    block_hash: str

    transaction_root: str

    state_root: str

    timestamp: float

    proposer: str

    def snapshot(self) -> dict:
        """
        Deterministic header snapshot.
        """

        return {
            "height":
                self.height,

            "previous_hash":
                self.previous_hash,

            "block_hash":
                self.block_hash,

            "transaction_root":
                self.transaction_root,

            "state_root":
                self.state_root,

            "timestamp":
                self.timestamp,

            "proposer":
                self.proposer,
        }