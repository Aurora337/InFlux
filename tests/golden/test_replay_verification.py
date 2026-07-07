"""Integration test for replay verification engine."""

import sys
sys.path.insert(0, "src")
sys.path.insert(0, "harness/replay-engine")

from influx.kernel.state import State
from influx.kernel.ledger.pipeline import process_pipeline
from influx.kernel.ledger.serialization import serialize_state
from influx.kernel.ledger.hash_sync import compute_root_hash
from replay_store import ReplayStore
from replay_runner import ReplayRunner
from replay_report import ReplayReportGenerator


def test_replay_verification_matches():
    """Record a state transition, then replay and verify hash integrity."""
    
    # Initial state
    state = State(epoch=0, supply=1000.0, participants=100)
    
    # Transition
    next_state = process_pipeline(state)
    
    # Compute hash
    serialized = serialize_state(next_state)
    state_hash = compute_root_hash(serialized)
    
    # Record in replay store
    store = ReplayStore()
    store.record(
        epoch=next_state.epoch,
        state_hash=state_hash,
        state_dict=next_state.to_dict(),
    )
    
    # Replay
    runner = ReplayRunner()
    snapshots = store.all_snapshots()
    runner.replay_all(snapshots)
    
    # Generate report
    generator = ReplayReportGenerator()
    report = generator.generate(runner.replay_results)
    
    # Assertions
    assert report.all_passed, f"Replay verification failed: {report.summary()}"
    assert report.matched_epochs == 1
    assert report.mismatched_epochs == 0
    assert len(report.details) == 1
    assert report.details[0]["recorded_hash"] == report.details[0]["recomputed_hash"]


def test_replay_verification_detects_mismatch():
    """Verify that replay detection catches hash mismatches."""
    
    state = State(epoch=0, supply=1000.0, participants=100)
    next_state = process_pipeline(state)
    
    # Compute correct hash
    serialized = serialize_state(next_state)
    correct_hash = compute_root_hash(serialized)
    
    # Store with tampered hash
    store = ReplayStore()
    store.record(
        epoch=next_state.epoch,
        state_hash="fake_hash_0000000000000000000000000000000000000000000000000000000000000000",
        state_dict=next_state.to_dict(),
    )
    
    # Replay
    runner = ReplayRunner()
    snapshots = store.all_snapshots()
    runner.replay_all(snapshots)
    
    # Generate report
    generator = ReplayReportGenerator()
    report = generator.generate(runner.replay_results)
    
    # Assertions
    assert not report.all_passed, "Should have detected mismatch"
    assert report.mismatched_epochs == 1
    assert report.matched_epochs == 0
