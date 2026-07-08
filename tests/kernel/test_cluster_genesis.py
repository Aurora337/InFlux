import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from influx.kernel.cluster import ClusterDetectionEngine, ClusterType, NodeRole, NodeSignal


def _signal(node_id: str, role: NodeRole, vpu: float, ctor_slot: int) -> NodeSignal:
    return NodeSignal(
        node_id=node_id,
        role=role,
        vpu=vpu,
        alignment_vector=(0.9, 0.9, 0.9, 0.9),
        ctor_slot=ctor_slot,
    )


def test_cluster_genesis_verification_cluster() -> None:
    engine = ClusterDetectionEngine()
    signals = [
        _signal("vn-1", NodeRole.VN, 5.0, 10),
        _signal("vn-2", NodeRole.VN, 4.0, 11),
        _signal("vn-3", NodeRole.VN, 3.0, 12),
    ]

    clusters = engine.form_clusters(signals)

    assert len(clusters) == 1
    assert clusters[0].cluster_type == ClusterType.VC
    assert clusters[0].lifecycle.value == "stable"
    assert clusters[0].state_score >= 0.0


def test_cluster_genesis_rejects_low_vpu() -> None:
    engine = ClusterDetectionEngine()
    signals = [
        _signal("ren-1", NodeRole.REN, 1.0, 3),
        _signal("ren-2", NodeRole.REN, 1.0, 4),
        _signal("ren-3", NodeRole.REN, 1.0, 5),
    ]

    clusters = engine.form_clusters(signals)
    assert clusters == []


def test_cluster_genesis_deterministic_output() -> None:
    engine = ClusterDetectionEngine()
    signals = [
        _signal("ptn-2", NodeRole.PTN, 6.0, 21),
        _signal("ptn-1", NodeRole.PTN, 5.0, 20),
    ]

    first = engine.form_clusters(signals)
    second = engine.form_clusters(signals)

    assert first == second
