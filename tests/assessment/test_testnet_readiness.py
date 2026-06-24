import json
import subprocess
from pathlib import Path

from runtime_executable import PYTHON_EXECUTABLE


REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_assessment(output_json: Path, output_md: Path) -> dict:
    result = subprocess.run(
        [
            PYTHON_EXECUTABLE,
            "scripts/assessment/testnet_readiness.py",
            "--output-json",
            str(output_json),
            "--output-md",
            str(output_md),
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert output_json.exists()
    assert output_md.exists()
    return json.loads(output_json.read_text(encoding="utf-8"))


def test_testnet_readiness_output_contract(tmp_path: Path):
    output_json = tmp_path / "testnet_readiness_score.json"
    output_md = tmp_path / "testnet_readiness_assessment.md"

    payload = _run_assessment(output_json, output_md)

    assert payload["testnet_ready"] is False
    assert payload["readiness_score"] == 0.64
    assert payload["consensus"] == 0.77
    assert payload["validator_lifecycle"] == 0.39
    assert payload["peer_discovery"] == 0.22
    assert payload["state_replication"] == 0.43
    assert payload["replay_engine"] == 0.88
    assert payload["ledger"] == 0.77
    assert payload["economics"] == 1.0



def test_testnet_readiness_blocking_domains(tmp_path: Path):
    output_json = tmp_path / "score.json"
    output_md = tmp_path / "assessment.md"

    payload = _run_assessment(output_json, output_md)
    assert payload["blocking_domains"] == [
        "validator_lifecycle",
        "peer_discovery",
        "state_replication",
    ]



def test_testnet_readiness_is_deterministic(tmp_path: Path):
    json_one = tmp_path / "one.json"
    md_one = tmp_path / "one.md"
    json_two = tmp_path / "two.json"
    md_two = tmp_path / "two.md"

    payload_one = _run_assessment(json_one, md_one)
    payload_two = _run_assessment(json_two, md_two)

    assert payload_one == payload_two
    assert md_one.read_text(encoding="utf-8") == md_two.read_text(encoding="utf-8")
