import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from influx.kernel.cluster import (
    ClusterDetectionEngine,
    ClusterLifecycle,
    ClusterState,
    ClusterType,
    ClusterThresholds,
)


def _cluster(
    cluster_id: str,
    nodes: tuple[str, ...],
    coherence: float,
    entropy: float,
    vpu_density: float,
) -> ClusterState:
    return ClusterState(
        cluster_id=cluster_id,
        cluster_type=ClusterType.HSC,
        lifecycle=ClusterLifecycle.STABLE,
        member_nodes=nodes,
        ctor_window=(10, 14),
        vpu_density=vpu_density,
        alignment_coherence=coherence,
        alignment_entropy=1.0 - coherence,
        node_entropy=entropy,
        reserve_pressure=0.1,
        state_score=0.8,
        diagnostics={},
    )


def test_merge_transition_deterministic() -> None:
    thresholds = ClusterThresholds(merge_alignment_threshold=0.7, merge_vpu_similarity_threshold=0.7)
    engine = ClusterDetectionEngine(thresholds=thresholds)
    left = _cluster("left", ("a", "b"), coherence=0.91, entropy=0.2, vpu_density=0.9)
    right = _cluster("right", ("c", "d"), coherence=0.92, entropy=0.2, vpu_density=0.91)

    merged_first = engine.evaluate_transitions([left, right])
    merged_second = engine.evaluate_transitions([left, right])

    assert merged_first == merged_second
    assert merged_first[0].lifecycle in {ClusterLifecycle.MERGING, ClusterLifecycle.STABLE}


def test_split_transition_deterministic() -> None:
    thresholds = ClusterThresholds(split_entropy_max=0.5)
    engine = ClusterDetectionEngine(thresholds=thresholds)
    unstable = _cluster("unstable", ("n1", "n2", "n3", "n4"), coherence=0.7, entropy=0.9, vpu_density=0.8)

    transitioned = engine.evaluate_transitions([unstable], ctor_stable=False)

    assert len(transitioned) == 1
    assert transitioned[0].lifecycle == ClusterLifecycle.SPLITTING
    assert transitioned[0].member_nodes == ("n1", "n2")
