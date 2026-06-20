import shutil
from pathlib import Path
import sys

sys.path.insert(0, "src")
sys.path.insert(0, "harness/replay-engine")

from kernel.state import State
from kernel.ledger.block_store import BlockStore
from kernel.ledger.pipeline import process_pipeline
from kernel.ledger.serialization import serialize_state
from kernel.ledger.hash_sync import compute_root_hash
from replay_audit import audit_ledger_replay


def _hash_state(state: State) -> str:
    return compute_root_hash(serialize_state(state))


def test_replay_audit_passes_for_valid_chain():
    test_dir = Path("data/blocks_replay_audit_test")
    if test_dir.exists():
        shutil.rmtree(test_dir)

    store = BlockStore(data_dir=str(test_dir))
    initial = State(epoch=0, supply=1000.0, participants=100)

    state = process_pipeline(initial)
    for _ in range(5):
        store.append(_hash_state(state))
        state = process_pipeline(state)

    report = audit_ledger_replay(initial_state=initial, data_dir=str(test_dir))

    assert report.blocks_checked == 5
    assert report.blocks_failed == 0
    assert report.blocks_passed == 5
    assert report.replay_success_rate == 1.0
    assert report.determinism_score == 1.0
    assert report.ledger_integrity == "PASS"

    shutil.rmtree(test_dir)


def test_replay_audit_detects_mismatch():
    test_dir = Path("data/blocks_replay_audit_mismatch")
    if test_dir.exists():
        shutil.rmtree(test_dir)

    store = BlockStore(data_dir=str(test_dir))
    initial = State(epoch=0, supply=1000.0, participants=100)

    good_state = process_pipeline(initial)
    store.append(_hash_state(good_state))
    store.append("deadbeef" * 8)

    report = audit_ledger_replay(initial_state=initial, data_dir=str(test_dir))

    assert report.blocks_checked == 2
    assert report.blocks_failed == 1
    assert report.blocks_passed == 1
    assert report.replay_success_rate == 0.5
    assert report.determinism_score == 0.5
    assert report.ledger_integrity == "FAIL"

    shutil.rmtree(test_dir)
