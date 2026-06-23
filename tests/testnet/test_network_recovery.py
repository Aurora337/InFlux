import json
from pathlib import Path

from scripts.testnet.network_recovery_validator import validate_network_recovery


def test_single_validator_recovery(tmp_path: Path) -> None:
    result = validate_network_recovery(
        validator_count=5,
        scenario="single_failure",
        fault_mode="none",
        snapshot_dir=tmp_path / "single",
    )
    assert result["network_recovery_valid"] is True
    assert result["validators_recovered"] == 5


def test_multi_validator_recovery(tmp_path: Path) -> None:
    result = validate_network_recovery(
        validator_count=5,
        scenario="multi_failure",
        fault_mode="drop_outbound",
        snapshot_dir=tmp_path / "multi",
    )
    assert result["network_recovery_valid"] is True
    assert result["recovery_score"] == 1.0


def test_full_network_restart(tmp_path: Path) -> None:
    result = validate_network_recovery(
        validator_count=5,
        scenario="full_restart",
        fault_mode="message_hash_mismatch",
        snapshot_dir=tmp_path / "full",
    )
    assert result["network_recovery_valid"] is True
    assert result["validators_expected"] == 5


def test_membership_restoration(tmp_path: Path) -> None:
    result = validate_network_recovery(
        validator_count=5,
        scenario="single_failure",
        fault_mode="none",
        snapshot_dir=tmp_path / "membership",
    )
    assert result["membership_restored"] is True


def test_consensus_restoration(tmp_path: Path) -> None:
    result = validate_network_recovery(
        validator_count=5,
        scenario="multi_failure",
        fault_mode="none",
        snapshot_dir=tmp_path / "consensus",
    )
    assert result["consensus_restored"] is True


def test_hash_consistency_after_recovery(tmp_path: Path) -> None:
    result = validate_network_recovery(
        validator_count=5,
        scenario="single_failure",
        fault_mode="none",
        snapshot_dir=tmp_path / "hash",
    )
    assert result["canonical_hash_consistent"] is True


def test_deterministic_output(tmp_path: Path) -> None:
    first = validate_network_recovery(
        validator_count=5,
        scenario="single_failure",
        fault_mode="none",
        snapshot_dir=tmp_path / "a",
    )
    second = validate_network_recovery(
        validator_count=5,
        scenario="single_failure",
        fault_mode="none",
        snapshot_dir=tmp_path / "b",
    )
    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
