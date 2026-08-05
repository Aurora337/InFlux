import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from influx.clusters.economic import (
    ClusterEconomicCouplingEngine,
    ClusterEconomicInput,
    merge_metric_continuity,
    split_metric_continuity,
)


def _snapshot(cluster_id: str, ren_share: float) -> ClusterEconomicInput:
    return ClusterEconomicInput(
        cluster_id=cluster_id,
        vpu_density=7.5,
        alignment_coherence=0.88,
        event_intensity=0.72,
        reserve_utilization=0.45,
        reserve_drift=0.25,
        cluster_entropy=0.18,
        role_composition={
            "VN": 0.3,
            "SN": 0.2,
            "REN": ren_share,
            "PTN": 0.15,
            "AN": 0.05,
        },
    )


def test_cluster_coupling_batch_deterministic_order_independent() -> None:
    engine = ClusterEconomicCouplingEngine()
    a = _snapshot("cluster-a", 0.3)
    b = _snapshot("cluster-b", 0.4)

    first = engine.compute_batch([a, b])
    second = engine.compute_batch([b, a])

    assert first == second


def test_cluster_merge_metric_continuity() -> None:
    engine = ClusterEconomicCouplingEngine()
    left = engine.compute_metrics(_snapshot("left", 0.3))
    right = engine.compute_metrics(_snapshot("right", 0.5))

    merged = merge_metric_continuity(
        left,
        right,
        left_weight=2.0,
        right_weight=3.0,
        merged_cluster_id="merged",
    )

    assert merged.cluster_id == "merged"
    assert 0.0 <= merged.demand_pressure <= 1.0
    assert 0.0 <= merged.reserve_pressure <= 1.0
    assert 0.0 <= merged.reproduction_pressure <= 1.0
    assert 0.0 <= merged.stability_index <= 1.0


def test_cluster_split_metric_continuity() -> None:
    engine = ClusterEconomicCouplingEngine()
    parent = engine.compute_metrics(_snapshot("parent", 0.35))

    left, right = split_metric_continuity(
        parent,
        left_ratio=0.6,
        left_cluster_id="child-left",
        right_cluster_id="child-right",
    )

    assert left.cluster_id == "child-left"
    assert right.cluster_id == "child-right"
    assert left.demand_pressure == parent.demand_pressure
    assert right.demand_pressure == parent.demand_pressure
    assert left.stability_index == parent.stability_index
    assert right.stability_index == parent.stability_index
