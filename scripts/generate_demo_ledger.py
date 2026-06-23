#!/usr/bin/env python3
"""Generate a deterministic demo ledger used by replay/cross-environment checks."""

from pathlib import Path
import shutil
import sys

sys.path.insert(0, "src")

from influx.kernel.state import State
from influx.kernel.ledger.pipeline import process_pipeline
from influx.kernel.ledger.serialization import serialize_state
from influx.kernel.ledger.hash_sync import compute_root_hash
from influx.kernel.ledger.block_store import BlockStore


def _hash_state(state: State) -> str:
    return compute_root_hash(serialize_state(state))


def main() -> int:
    target = Path("data/blocks_demo_verify")
    if target.exists():
        shutil.rmtree(target)

    store = BlockStore(data_dir=str(target))

    state = process_pipeline(State(epoch=0, supply=1000.0, participants=100))
    for _ in range(3):
        store.append(_hash_state(state))
        state = process_pipeline(state)

    print(f"demo ledger generated with {store.chain_height()} blocks at {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
