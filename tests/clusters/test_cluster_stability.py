import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from influx.clusters.economic.stability import compute_stability_index


def test_cluster_stability_bounds() -> None:
    score = compute_stability_index(
        alignment_coherence=0.85,
        reserve_pressure=0.4,
        demand_pressure=0.7,
        reproduction_pressure=0.68,
        cluster_entropy=0.2,
    )
    assert 0.0 <= score <= 1.0


def test_cluster_stability_increases_with_coherence() -> None:
    low = compute_stability_index(
        alignment_coherence=0.4,
        reserve_pressure=0.3,
        demand_pressure=0.6,
        reproduction_pressure=0.6,
        cluster_entropy=0.2,
    )
    high = compute_stability_index(
        alignment_coherence=0.9,
        reserve_pressure=0.3,
        demand_pressure=0.6,
        reproduction_pressure=0.6,
        cluster_entropy=0.2,
    )
    assert high > low
