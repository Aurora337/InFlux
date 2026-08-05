import json
import subprocess

from scripts.testnet.peer_discovery import validate_peer_discovery


def test_peer_discovery_output_contract() -> None:
    result = validate_peer_discovery(peer_count=5)
    assert result["peer_discovery_valid"] is True
    assert result["peers_found"] == 5
    assert result["membership_consistent"] is True


def test_peer_discovery_cli_output() -> None:
    run = subprocess.run(
        ["python", "scripts/testnet/peer_discovery.py"],
        cwd="/workspaces/InFlux",
        capture_output=True,
        text=True,
    )
    assert run.returncode == 0, run.stderr
    payload = json.loads(run.stdout)
    assert payload["peer_discovery_valid"] is True
    assert payload["peers_found"] == 5
    assert payload["membership_consistent"] is True


def test_peer_discovery_is_deterministic() -> None:
    first = validate_peer_discovery(peer_count=5)
    second = validate_peer_discovery(peer_count=5)
    assert first == second
