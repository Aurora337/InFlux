import json
from pathlib import Path
import subprocess

import pytest

from scripts.testnet.multi_node_persistence import PersistenceError, validate_multi_node_persistence


def test_persist_state_files_created(tmp_path: Path) -> None:
    state_dir = tmp_path / "state"
    result = validate_multi_node_persistence(node_count=5, state_dir=state_dir)
    persisted = sorted(state_dir.glob("validator-*.json"))

    assert len(persisted) == 5
    assert result["nodes_persisted"] == 5


def test_restart_recovery_matches_persisted_state(tmp_path: Path) -> None:
    state_dir = tmp_path / "state"
    result = validate_multi_node_persistence(node_count=5, state_dir=state_dir)

    assert result["restart_recovery_valid"] is True
    assert result["state_hash_consistent"] is True


def test_output_contract(tmp_path: Path) -> None:
    state_dir = tmp_path / "state"
    result = validate_multi_node_persistence(node_count=5, state_dir=state_dir)

    assert result == {
        "persistence_valid": True,
        "nodes_persisted": 5,
        "durable_write_valid": True,
        "restart_recovery_valid": True,
        "state_hash_consistent": True,
    }


def test_deterministic_output(tmp_path: Path) -> None:
    first_dir = tmp_path / "state-a"
    second_dir = tmp_path / "state-b"

    first = validate_multi_node_persistence(node_count=5, state_dir=first_dir)
    second = validate_multi_node_persistence(node_count=5, state_dir=second_dir)

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_invalid_node_count_rejected(tmp_path: Path) -> None:
    with pytest.raises(PersistenceError):
        validate_multi_node_persistence(node_count=0, state_dir=tmp_path / "state")


def test_cli_output(tmp_path: Path) -> None:
    run = subprocess.run(
        [
            "python3",
            "scripts/testnet/multi_node_persistence.py",
            "--state-dir",
            str(tmp_path / "state"),
        ],
        cwd="/workspaces/InFlux",
        capture_output=True,
        text=True,
    )
    assert run.returncode == 0, run.stderr

    payload = json.loads(run.stdout)
    assert payload["persistence_valid"] is True
    assert payload["nodes_persisted"] == 5
