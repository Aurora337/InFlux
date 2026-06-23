import json
from pathlib import Path
import subprocess

from scripts.testnet.peer_discovery import validate_peer_discovery


def _write_artifacts(base_dir: Path, peers: list[str], validators: list[str], expected_peer_count: int = 5) -> tuple[Path, Path, Path]:
    peers_dir = base_dir / "testnet" / "peers"
    validators_dir = base_dir / "testnet" / "validators"
    launch_dir = base_dir / "testnet" / "launch"

    peers_dir.mkdir(parents=True, exist_ok=True)
    validators_dir.mkdir(parents=True, exist_ok=True)
    launch_dir.mkdir(parents=True, exist_ok=True)

    peers_payload = {
        "peers": [{"peer_id": peer_id} for peer_id in peers],
    }
    (peers_dir / "peers.json").write_text(json.dumps(peers_payload, indent=2), encoding="utf-8")

    for validator_id in validators:
        payload = {"peer_id": validator_id, "validator_id": validator_id}
        (validators_dir / f"{validator_id}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    network_health = {
        "expected_peer_count": expected_peer_count,
        "network_healthy": True,
        "healthy_peers": list(dict.fromkeys(peers)),
    }
    (launch_dir / "network_health.json").write_text(json.dumps(network_health, indent=2), encoding="utf-8")

    return peers_dir / "peers.json", validators_dir, launch_dir / "network_health.json"


def test_peer_registry_load(tmp_path: Path) -> None:
    peers_path, validators_dir, network_health_path = _write_artifacts(
        tmp_path,
        peers=["peer-1", "peer-2", "peer-3", "peer-4", "peer-5"],
        validators=["peer-1", "peer-2", "peer-3", "peer-4", "peer-5"],
    )
    result = validate_peer_discovery(
        peer_count=5,
        peers_path=peers_path,
        validators_dir=validators_dir,
        network_health_path=network_health_path,
    )
    assert result["peers_found"] == 5


def test_peer_count_matches_expected(tmp_path: Path) -> None:
    peers_path, validators_dir, network_health_path = _write_artifacts(
        tmp_path,
        peers=["peer-1", "peer-2", "peer-3", "peer-4", "peer-5"],
        validators=["peer-1", "peer-2", "peer-3", "peer-4", "peer-5"],
        expected_peer_count=5,
    )
    result = validate_peer_discovery(
        peer_count=5,
        peers_path=peers_path,
        validators_dir=validators_dir,
        network_health_path=network_health_path,
    )
    assert result["peers_found"] == 5
    assert result["missing_peers"] == 0


def test_membership_consistency(tmp_path: Path) -> None:
    peers_path, validators_dir, network_health_path = _write_artifacts(
        tmp_path,
        peers=["peer-1", "peer-2", "peer-3", "peer-4", "peer-5"],
        validators=["peer-1", "peer-2", "peer-3", "peer-4", "peer-5"],
    )
    result = validate_peer_discovery(
        peer_count=5,
        peers_path=peers_path,
        validators_dir=validators_dir,
        network_health_path=network_health_path,
    )
    assert result["membership_consistent"] is True


def test_duplicate_peer_detection(tmp_path: Path) -> None:
    peers_path, validators_dir, network_health_path = _write_artifacts(
        tmp_path,
        peers=["peer-1", "peer-2", "peer-3", "peer-4", "peer-5", "peer-5"],
        validators=["peer-1", "peer-2", "peer-3", "peer-4", "peer-5"],
    )
    result = validate_peer_discovery(
        peer_count=5,
        peers_path=peers_path,
        validators_dir=validators_dir,
        network_health_path=network_health_path,
    )
    assert result["duplicate_peers"] == 1
    assert result["peer_discovery_valid"] is False


def test_missing_peer_detection(tmp_path: Path) -> None:
    peers_path, validators_dir, network_health_path = _write_artifacts(
        tmp_path,
        peers=["peer-1", "peer-2", "peer-3", "peer-4"],
        validators=["peer-1", "peer-2", "peer-3", "peer-4", "peer-5"],
    )
    result = validate_peer_discovery(
        peer_count=5,
        peers_path=peers_path,
        validators_dir=validators_dir,
        network_health_path=network_health_path,
    )
    assert result["missing_peers"] == 1
    assert result["peer_discovery_valid"] is False


def test_deterministic_output(tmp_path: Path) -> None:
    peers_path, validators_dir, network_health_path = _write_artifacts(
        tmp_path,
        peers=["peer-1", "peer-2", "peer-3", "peer-4", "peer-5"],
        validators=["peer-1", "peer-2", "peer-3", "peer-4", "peer-5"],
    )
    first = validate_peer_discovery(
        peer_count=5,
        peers_path=peers_path,
        validators_dir=validators_dir,
        network_health_path=network_health_path,
    )
    second = validate_peer_discovery(
        peer_count=5,
        peers_path=peers_path,
        validators_dir=validators_dir,
        network_health_path=network_health_path,
    )
    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_peer_discovery_cli_output() -> None:
    run = subprocess.run(
        ["python3", "scripts/testnet/peer_discovery.py"],
        cwd="/workspaces/InFlux",
        capture_output=True,
        text=True,
    )
    assert run.returncode == 0, run.stderr
    payload = json.loads(run.stdout)
    assert payload == {
        "peer_discovery_valid": True,
        "peers_found": 5,
        "membership_consistent": True,
        "duplicate_peers": 0,
        "missing_peers": 0,
    }
