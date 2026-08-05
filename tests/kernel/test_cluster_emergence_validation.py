import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from influx.kernel.cluster.simulation import default_event_stream, run_cluster_emergence_simulation
from influx.kernel.cluster.validation import validate_cluster_emergence_report


def test_validation_accepts_deterministic_report() -> None:
    report = run_cluster_emergence_simulation(default_event_stream())
    result = validate_cluster_emergence_report(report)
    assert result["report_valid"] is True
    assert result["checks_failed"] == 0


def test_validation_rejects_tampered_report() -> None:
    report = run_cluster_emergence_simulation(default_event_stream())
    report["windows"][0]["clusters"][0]["state_score"] = 2.5
    result = validate_cluster_emergence_report(report)
    assert result["report_valid"] is False
    assert any("state_score_bounds" in check for check in result["failed_checks"])


def test_validation_cli_and_pipeline(tmp_path: Path) -> None:
    report_json = tmp_path / "sim_report.json"
    report_md = tmp_path / "sim_report.md"
    validation_json = tmp_path / "sim_validation.json"
    validation_md = tmp_path / "sim_validation.md"
    pipeline_json = tmp_path / "sim_pipeline.json"
    pipeline_md = tmp_path / "sim_pipeline.md"

    simulate = subprocess.run(
        [
            sys.executable,
            "scripts/testnet/simulate_cluster_emergence.py",
            "--output",
            str(report_json),
            "--markdown-output",
            str(report_md),
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert simulate.returncode == 0, simulate.stderr

    validate = subprocess.run(
        [
            sys.executable,
            "scripts/testnet/validate_cluster_emergence.py",
            "--input",
            str(report_json),
            "--output",
            str(validation_json),
            "--markdown-output",
            str(validation_md),
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert validate.returncode == 0, validate.stderr

    pipeline = subprocess.run(
        [
            sys.executable,
            "scripts/testnet/run_cluster_emergence_validation_pipeline.py",
            "--output-json",
            str(pipeline_json),
            "--output-md",
            str(pipeline_md),
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert pipeline.returncode == 0, pipeline.stderr

    payload = json.loads(pipeline_json.read_text(encoding="utf-8"))
    assert payload["pipeline_success"] is True
    assert payload["summary"]["replay_match"] is True
    assert payload["summary"]["validation_passed"] is True
