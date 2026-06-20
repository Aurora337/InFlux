"""Replay audit utilities for full-ledger determinism verification."""

from dataclasses import dataclass
import sys

sys.path.insert(0, "src")

from kernel.state import State
from kernel.ledger.block_store import BlockStore
from kernel.ledger.pipeline import process_pipeline
from kernel.ledger.serialization import serialize_state
from kernel.ledger.hash_sync import compute_root_hash


@dataclass
class BlockAuditResult:
    block_height: int
    stored_hash: str
    replay_hash: str
    passed: bool


@dataclass
class ReplayAuditReport:
    genesis_hash: str
    blocks_checked: int
    blocks_passed: int
    blocks_failed: int
    replay_success_rate: float
    determinism_score: float
    ledger_integrity: str
    details: list[BlockAuditResult]

    def to_dict(self) -> dict:
        return {
            "genesis_hash": self.genesis_hash,
            "blocks_checked": self.blocks_checked,
            "blocks_passed": self.blocks_passed,
            "blocks_failed": self.blocks_failed,
            "replay_success_rate": self.replay_success_rate,
            "determinism_score": self.determinism_score,
            "ledger_integrity": self.ledger_integrity,
            "details": [
                {
                    "block_height": item.block_height,
                    "stored_hash": item.stored_hash,
                    "replay_hash": item.replay_hash,
                    "passed": item.passed,
                }
                for item in self.details
            ],
        }


def _hash_state(state: State) -> str:
    return compute_root_hash(serialize_state(state))


def audit_ledger_replay(
    initial_state: State,
    data_dir: str = "data/blocks",
) -> ReplayAuditReport:
    """Replay from genesis and verify each stored block hash deterministically."""
    store = BlockStore(data_dir=data_dir)
    chain = store.all_blocks()

    genesis_hash = _hash_state(initial_state)

    if not chain:
        return ReplayAuditReport(
            genesis_hash=genesis_hash,
            blocks_checked=0,
            blocks_passed=0,
            blocks_failed=0,
            replay_success_rate=0.0,
            determinism_score=0.0,
            ledger_integrity="PASS",
            details=[],
        )

    chain_integrity_ok = store.verify_chain()

    initial_hash = genesis_hash
    first_transition_state = process_pipeline(initial_state)
    first_transition_hash = _hash_state(first_transition_state)

    if chain[0].state_hash == initial_hash:
        replay_state = initial_state
    elif chain[0].state_hash == first_transition_hash:
        replay_state = first_transition_state
    else:
        replay_state = initial_state

    details: list[BlockAuditResult] = []
    for block in chain:
        replay_hash = _hash_state(replay_state)
        passed = replay_hash == block.state_hash
        details.append(
            BlockAuditResult(
                block_height=block.height,
                stored_hash=block.state_hash,
                replay_hash=replay_hash,
                passed=passed,
            )
        )
        replay_state = process_pipeline(replay_state)

    blocks_checked = len(details)
    blocks_passed = sum(1 for item in details if item.passed)
    blocks_failed = blocks_checked - blocks_passed
    replay_success_rate = blocks_passed / blocks_checked if blocks_checked else 0.0
    determinism_score = replay_success_rate
    ledger_integrity = "PASS" if (chain_integrity_ok and blocks_failed == 0) else "FAIL"

    return ReplayAuditReport(
        genesis_hash=genesis_hash,
        blocks_checked=blocks_checked,
        blocks_passed=blocks_passed,
        blocks_failed=blocks_failed,
        replay_success_rate=replay_success_rate,
        determinism_score=determinism_score,
        ledger_integrity=ledger_integrity,
        details=details,
    )


__all__ = ["BlockAuditResult", "ReplayAuditReport", "audit_ledger_replay"]
