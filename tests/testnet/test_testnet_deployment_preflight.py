import json
import subprocess
from pathlib import Path

from runtime_executable import python_cmd
from scripts.testnet.validate_testnet_deployment_preflight import run_preflight


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_script(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/usr/bin/env python3\nprint('ok')\n", encoding="utf-8")
    path.chmod(0o755)


def _build_valid_tree(root: Path) -> None:
    _write_json(root / "testnet" / "configs" / "network.json", {"network": "dev"})
    _write_json(root / "testnet" / "genesis" / "genesis.json", {"height": 0})
    _write_json(root / "testnet" / "validators" / "validator_1.json", {"validator_id": "validator-1"})

    _write_script(root / "scripts" / "testnet" / "bootstrap_network.py")
    _write_script(root / "scripts" / "testnet" / "launch_validator.py")
    _write_script(root / "scripts" / "testnet" / "validator_lifecycle.py")


def _run_cli(root: Path, out: Path, min_validators: int = 1) -> subprocess.CompletedProcess:
    repo_root = Path(__file__).resolve().parents[2]
    return subprocess.run(
        python_cmd(
            "scripts/testnet/validate_testnet_deployment_preflight.py",
            "--root",
            str(root),
            "--min-validators",
            str(min_validators),
            "--output",
            str(out),
        ),
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )


def _without_timestamp(report: dict) -> dict:
    trimmed = dict(report)
    trimmed.pop("timestamp", None)
    return trimmed


def test_preflight_report_schema_success(tmp_path: Path) -> None:
    _build_valid_tree(tmp_path)
    output = tmp_path / "report.json"

    run = _run_cli(tmp_path, output, min_validators=1)

    assert run.returncode == 0, run.stderr
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert payload["preflight_valid"] is True
    assert payload["preflight_score"] == 1.0
    assert payload["checks_passed"] == payload["checks_total"]
    assert isinstance(payload["input_fingerprint"], str)
    assert len(payload["input_fingerprint"]) == 64
    assert payload["timestamp"].endswith("Z")

    for key in [
        "required_directories",
        "json_parse_valid",
        "validator_count_threshold",
        "unique_validator_identity",
        "required_launch_scripts",
    ]:
        assert key in payload["checks"]
        assert isinstance(payload["checks"][key]["valid"], bool)
        assert isinstance(payload["checks"][key]["message"], str)


def test_preflight_deterministic_output(tmp_path: Path) -> None:
    _build_valid_tree(tmp_path)

    first = run_preflight(root=tmp_path, min_validators=1)
    second = run_preflight(root=tmp_path, min_validators=1)

    assert _without_timestamp(first) == _without_timestamp(second)


def test_preflight_fails_on_invalid_json(tmp_path: Path) -> None:
    _build_valid_tree(tmp_path)
    (tmp_path / "testnet" / "genesis" / "broken.json").write_text("{broken", encoding="utf-8")

    report = run_preflight(root=tmp_path, min_validators=1)

    assert report["preflight_valid"] is False
    assert report["checks"]["json_parse_valid"]["valid"] is False


def test_preflight_fails_on_duplicate_validator_identity(tmp_path: Path) -> None:
    _build_valid_tree(tmp_path)
    _write_json(tmp_path / "testnet" / "validators" / "validator_2.json", {"validator_id": "validator-1"})

    report = run_preflight(root=tmp_path, min_validators=1)

    assert report["preflight_valid"] is False
    assert report["checks"]["unique_validator_identity"]["valid"] is False


def test_preflight_fails_on_missing_required_directory(tmp_path: Path) -> None:
    _build_valid_tree(tmp_path)
    for child in (tmp_path / "testnet" / "genesis").iterdir():
        child.unlink()
    (tmp_path / "testnet" / "genesis").rmdir()

    report = run_preflight(root=tmp_path, min_validators=1)

    assert report["preflight_valid"] is False
    assert report["checks"]["required_directories"]["valid"] is False
