import json
import subprocess

from scripts.testnet.state_replication_validator import validate_state_replication


def test_state_replication_output_contract() -> None:
    result = validate_state_replication(node_count=5)
    assert result["replication_valid"] is True
    assert result["agreement_rate"] == 1.0
    assert result["recovery_valid"] is True


def test_state_replication_cli_output() -> None:
    run = subprocess.run(
        ["python", "scripts/testnet/state_replication_validator.py"],
        cwd="/workspaces/InFlux",
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
