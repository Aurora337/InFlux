import json
from pathlib import Path

from scripts.testnet.node_recovery_validator import validate_node_recovery


def test_clean_restart(tmp_path: Path) -> None:
    result = validate_node_recovery(node_count=5, snapshot_dir=tmp_path / "state", fault_mode="none")
    assert result["recovery_valid"] is True
    assert result["restart_success_rate"] == 1.0


def test_restart_restores_state(tmp_path: Path) -> None:
    result = validate_node_recovery(node_count=5, snapshot_dir=tmp_path / "state", fault_mode="none")
    assert result["state_restored"] is True


def test_restart_restores_hash(tmp_path: Path) -> None:
    result = validate_node_recovery(node_count=5, snapshot_dir=tmp_path / "state", fault_mode="none")
    assert result["hash_consistent"] is True


def test_peer_membership_recovery(tmp_path: Path) -> None:
    result = validate_node_recovery(node_count=5, snapshot_dir=tmp_path / "state", fault_mode="unexpected_shutdown")
    assert result["peer_membership_restored"] is True


def test_missing_snapshot_detection(tmp_path: Path) -> None:
    result = validate_node_recovery(node_count=5, snapshot_dir=tmp_path / "state", fault_mode="missing_snapshot")
    assert result["missing_snapshot_detected"] is True
    assert result["recovery_valid"] is False


def test_corrupted_snapshot_detection(tmp_path: Path) -> None:
    result = validate_node_recovery(node_count=5, snapshot_dir=tmp_path / "state", fault_mode="corrupted_snapshot")
    assert result["corrupted_snapshot_detected"] is True
    assert result["recovery_valid"] is False


def test_deterministic_output(tmp_path: Path) -> None:
    first = validate_node_recovery(node_count=5, snapshot_dir=tmp_path / "state-a", fault_mode="none")
    second = validate_node_recovery(node_count=5, snapshot_dir=tmp_path / "state-b", fault_mode="none")

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
