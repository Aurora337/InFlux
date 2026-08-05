"""
Deterministic execution context for the InFlux Economic Core.

Provides the context object that carries block height, state root,
timestamps, and other execution metadata through the economic pipeline.
No economic rules or policies are defined here.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass(slots=True)
class EconomicContext:
    """
    Deterministic execution context for economic operations.

    Carries immutable context through the economic pipeline:
    - block_height: Current block height
    - block_timestamp: Block timestamp (deterministic from consensus)
    - state_root: Current state root hash
    - epoch: Current epoch number
    - round: Current consensus round
    - proposer: Block proposer identifier
    - chain_id: Chain/network identifier
    - previous_state_root: State root before this block's execution

    This context is read-only during execution and is set once
    at the beginning of each block's economic processing.
    """

    block_height: int
    block_timestamp: int
    state_root: str = ""
    epoch: int = 0
    round: int = 0
    proposer: str = ""
    chain_id: str = "influx-mainnet"
    previous_state_root: str = ""
    _hash: Optional[str] = field(default=None, repr=False)

    def compute_hash(self) -> str:
        """Compute deterministic context hash."""
        canonical = {
            "block_height": self.block_height,
            "block_timestamp": self.block_timestamp,
            "state_root": self.state_root,
            "epoch": self.epoch,
            "round": self.round,
            "proposer": self.proposer,
            "chain_id": self.chain_id,
            "previous_state_root": self.previous_state_root,
        }
        serialized = json.dumps(
            canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @property
    def hash(self) -> str:
        """Return cached or computed hash."""
        if self._hash is None:
            self._hash = self.compute_hash()
        return self._hash

    def snapshot(self) -> dict[str, Any]:
        """Deterministic context snapshot."""
        return {
            "block_height": self.block_height,
            "block_timestamp": self.block_timestamp,
            "state_root": self.state_root,
            "epoch": self.epoch,
            "round": self.round,
            "proposer": self.proposer,
            "chain_id": self.chain_id,
            "previous_state_root": self.previous_state_root,
            "hash": self.hash,
        }


def create_economic_context(
    block_height: int,
    block_timestamp: Optional[int] = None,
    state_root: str = "",
    epoch: int = 0,
    round: int = 0,
    proposer: str = "",
    chain_id: str = "influx-mainnet",
    previous_state_root: str = "",
) -> EconomicContext:
    """
    Factory function to create a deterministic economic context.

    Args:
        block_height: Current block height
        block_timestamp: Block timestamp (defaults to current UTC time)
        state_root: Current state root hash
        epoch: Current epoch number
        round: Current consensus round
        proposer: Block proposer identifier
        chain_id: Chain/network identifier
        previous_state_root: State root before this block

    Returns:
        A new EconomicContext
    """
    if block_timestamp is None:
        block_timestamp = int(datetime.now(timezone.utc).timestamp())

    return EconomicContext(
        block_height=block_height,
        block_timestamp=block_timestamp,
        state_root=state_root,
        epoch=epoch,
        round=round,
        proposer=proposer,
        chain_id=chain_id,
        previous_state_root=previous_state_root,
    )
