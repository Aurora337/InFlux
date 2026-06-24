from __future__ import annotations

from .cluster_equations import vpu_stream_similarity
from .cluster_types import ClusterState, ClusterThresholds


def can_merge(left: ClusterState, right: ClusterState, thresholds: ClusterThresholds) -> bool:
    alignment_overlap = min(left.alignment_coherence, right.alignment_coherence)
    stream_similarity = vpu_stream_similarity([left.vpu_density], [right.vpu_density])
    return (
        alignment_overlap >= thresholds.merge_alignment_threshold
        and stream_similarity >= thresholds.merge_vpu_similarity_threshold
    )


def must_split(cluster: ClusterState, thresholds: ClusterThresholds, ctor_stable: bool) -> bool:
    return cluster.node_entropy > thresholds.split_entropy_max or not ctor_stable


def deterministic_split_nodes(member_nodes: tuple[str, ...]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    ordered = tuple(sorted(member_nodes))
    midpoint = len(ordered) // 2
    if midpoint == 0:
        return ordered, tuple()
    return ordered[:midpoint], ordered[midpoint:]
