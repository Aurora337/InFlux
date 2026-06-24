import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from influx.kernel.cluster import NodeRole
from influx.kernel.cluster.simulation import ClusterEvent, default_event_stream, run_cluster_emergence_simulation


def test_simulation_deterministic_report() -> None:
    events = default_event_stream()
    first = run_cluster_emergence_simulation(events)
    second = run_cluster_emergence_simulation(events)
    assert first == second


def test_simulation_detects_expected_cluster_types() -> None:
    events = [
        ClusterEvent("e-1", "vn-1", NodeRole.VN, 6.0, (0.9, 0.9, 0.9, 0.9), 0, 0.1),
        ClusterEvent("e-2", "vn-2", NodeRole.VN, 5.0, (0.9, 0.9, 0.9, 0.9), 1, 0.1),
        ClusterEvent("e-3", "ren-1", NodeRole.REN, 6.0, (0.9, 0.9, 0.9, 0.9), 8, 0.2),
        ClusterEvent("e-4", "ren-2", NodeRole.REN, 5.0, (0.9, 0.9, 0.9, 0.9), 9, 0.2),
    ]

    report = run_cluster_emergence_simulation(events)

    assert report["simulation_valid"] is True
    assert report["cluster_type_counts"]["verification_cluster"] >= 1
    assert report["cluster_type_counts"]["economic_cluster"] >= 1


def test_cluster_emergence_cli_output(tmp_path: Path) -> None:
    output_json = tmp_path / "cluster_emergence.json"
    output_md = tmp_path / "cluster_emergence.md"

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/testnet/simulate_cluster_emergence.py",
            "--output",
            str(output_json),
            "--markdown-output",
            str(output_md),
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(output_json.read_text(encoding="utf-8"))

    assert payload["simulation_valid"] is True
    assert payload["event_count"] > 0
    assert payload["window_count"] > 0
    assert output_md.exists()
