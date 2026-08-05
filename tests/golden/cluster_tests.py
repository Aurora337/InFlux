import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from influx.clusters.economic import ClusterEconomicCouplingEngine, ClusterEconomicInput


def test_cluster_metrics_golden_determinism() -> None:
    engine = ClusterEconomicCouplingEngine()
    snapshot = ClusterEconomicInput(
        cluster_id="golden-cluster-1",
        vpu_density=8.0,
        alignment_coherence=0.9,
        event_intensity=0.7,
        reserve_utilization=0.4,
        reserve_drift=0.2,
        cluster_entropy=0.1,
        role_composition={"VN": 0.35, "SN": 0.2, "REN": 0.3, "PTN": 0.1, "AN": 0.05},
    )

    first = engine.compute_metrics(snapshot)
    second = engine.compute_metrics(snapshot)

    assert first == second
    assert 0.0 <= first.demand_pressure <= 1.0
    assert 0.0 <= first.reserve_pressure <= 1.0
    assert 0.0 <= first.reproduction_pressure <= 1.0
    assert 0.0 <= first.stability_index <= 1.0
