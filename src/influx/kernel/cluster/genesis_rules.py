from __future__ import annotations

from collections import Counter

from .cluster_equations import alignment_entropy, ctor_ordering_stable
from .cluster_types import ClusterThresholds, ClusterType, NodeRole, NodeSignal


def classify_cluster_type(signals: list[NodeSignal]) -> ClusterType:
    if not signals:
        return ClusterType.HSC

    counts = Counter(signal.role for signal in signals)
    total = float(len(signals))

    if float(counts.get(NodeRole.VN, 0)) / total >= 0.6:
        return ClusterType.VC
    if float(counts.get(NodeRole.REN, 0)) / total >= 0.6:
        return ClusterType.EC
    if float(counts.get(NodeRole.PTN, 0)) / total >= 0.6:
        return ClusterType.PC
    return ClusterType.HSC


def cluster_genesis_valid(signals: list[NodeSignal], thresholds: ClusterThresholds) -> bool:
    if not signals:
        return False
    vpu_sum = sum(max(0.0, signal.vpu) for signal in signals)
    return (
        vpu_sum >= thresholds.tau_cluster
        and alignment_entropy(signals) <= thresholds.epsilon_alignment_entropy
        and ctor_ordering_stable(signals)
    )
