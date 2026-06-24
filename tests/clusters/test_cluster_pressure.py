import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from influx.clusters.economic.pressure import (
    compute_demand_pressure,
    compute_reproduction_pressure,
    compute_reserve_pressure,
)


def test_cluster_pressure_bounds() -> None:
    demand = compute_demand_pressure(vpu_density=8.0, alignment_coherence=0.9, event_intensity=0.8)
    reserve = compute_reserve_pressure(reserve_utilization=0.7, reserve_drift=0.6)
    reproduction = compute_reproduction_pressure(vpu_density=8.0, ren_share=0.5, demand_pressure=demand)

    assert 0.0 <= demand <= 1.0
    assert 0.0 <= reserve <= 1.0
    assert 0.0 <= reproduction <= 1.0


def test_cluster_pressure_deterministic() -> None:
    first = compute_demand_pressure(vpu_density=6.0, alignment_coherence=0.8, event_intensity=0.6)
    second = compute_demand_pressure(vpu_density=6.0, alignment_coherence=0.8, event_intensity=0.6)
    assert first == second
