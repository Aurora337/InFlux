"""Persistent block storage for deterministic ledger."""

import json
from pathlib import Path
from typing import Optional
from time import time

from influx.kernel.ledger.block import Block 


class BlockStore:
    def __init__(self, data_dir: str = "data/blocks"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.blocks: list[Block] = []
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        """Load all blocks from disk on initialization."""
        if not self.data_dir.exists():
            return

        block_files = sorted(self.data_dir.glob("block_*.json"))
        for block_file in block_files:
            with open(block_file, "r") as f:
                data = json.load(f)
                self.blocks.append(Block.from_dict(data))

    def _save_to_disk(self, block: Block) -> None:
        """Persist a block to disk."""
        block_file = self.data_dir / f"block_{block.height:06d}.json"
        with open(block_file, "w") as f:
            json.dump(block.to_dict(), f, indent=2)

    def append(self, state_hash: str) -> Block:
        """Append a new block to the chain."""
        if len(self.blocks) == 0:
            block = Block.genesis(state_hash)
        else:
            previous_block = self.blocks[-1]
            block = Block(
                height=previous_block.height + 1,
                previous_hash=previous_block.state_hash,
                state_hash=state_hash,
                timestamp=time(),
            )

        self.blocks.append(block)
        self._save_to_disk(block)
        return block

    def get_block(self, height: int) -> Optional[Block]:
        """Retrieve a block by height."""
        if 0 <= height < len(self.blocks):
            return self.blocks[height]
        return None

    def get_latest_block(self) -> Optional[Block]:
        """Get the most recent block."""
        return self.blocks[-1] if self.blocks else None

    def chain_height(self) -> int:
        """Get the current height of the chain."""
        return len(self.blocks)

    def all_blocks(self) -> list[Block]:
        """Return all blocks in the chain."""
        return self.blocks[:]

    def verify_chain(self) -> bool:
        """Verify that the block chain is valid (each block links correctly)."""
        if len(self.blocks) == 0:
            return True

        for i, block in enumerate(self.blocks):
            if block.height != i:
                return False

            if i == 0:
                if block.previous_hash != "0" * 64:
                    return False
            else:
                if block.previous_hash != self.blocks[i - 1].state_hash:
                    return False

        return True


__all__ = ["BlockStore"]
