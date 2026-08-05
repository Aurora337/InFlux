import json
import subprocess
from pathlib import Path

import pytest

from influx.runtime_executable import python_cmd
from scripts.testnet.state_replication_validator import StateReplicationError, validate_state_replication


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_state_replication_output_contract() -> None:
    result = validate_state_replication(node_count=5)
    assert result == {
        "replication_valid": True,
        "agreement_rate": 1.0,
        "recovery_valid": True,
        "snapshot_exchange": True,
        "nodes_validated": 5,
        "canonical_state_hash": result["canonical_state_hash"],
        "recovery_replay": True,
        "replay_steps": 3,
    }
    assert len(result["canonical_state_hash"]) == 64


def test_state_replication_cli_output() -> None:
    run = subprocess.run(
        python_cmd("scripts/testnet/state_replication_validator.py"),
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert run.returncode == 0, run.stderr
    payload = json.loads(run.stdout)
    assert payload["replication_valid"] is True
    assert payload["agreement_rate"] == 1.0
    assert payload["recovery_valid"] is True


def test_state_replication_is_deterministic() -> None:
    first = validate_state_replication(node_count=5)
    second = validate_state_replication(node_count=5)
    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_state_replication_rejects_invalid_node_count() -> None:
    with pytest.raises(StateReplicationError):
        validate_state_replication(node_count=0)
