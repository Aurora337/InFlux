from __future__ import annotations

import math
from collections import Counter

from .cluster_types import NodeSignal, NodeRole


def _dot(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _norm(a: tuple[float, ...]) -> float:
    return math.sqrt(sum(x * x for x in a))


def _cosine_similarity(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    denom = _norm(a) * _norm(b)
    if denom == 0.0:
        return 0.0
    return max(0.0, min(1.0, _dot(a, b) / denom))


def vpu_density(signals: list[NodeSignal]) -> float:
    if not signals:
        return 0.0
    total_vpu = sum(max(0.0, s.vpu) for s in signals)
    return total_vpu / max(1.0, float(len(signals)))


def alignment_coherence(signals: list[NodeSignal]) -> float:
    if len(signals) < 2:
        return 1.0 if signals else 0.0

    sims: list[float] = []
    for idx, left in enumerate(signals):
        for right in signals[idx + 1 :]:
            sims.append(_cosine_similarity(left.alignment_vector, right.alignment_vector))
    return sum(sims) / float(len(sims)) if sims else 0.0


def alignment_entropy(signals: list[NodeSignal]) -> float:
    return max(0.0, 1.0 - alignment_coherence(signals))


def node_entropy(signals: list[NodeSignal]) -> float:
    if not signals:
        return 1.0

    counts = Counter(s.role for s in signals)
    total = float(sum(counts.values()))
    entropy = 0.0
    for count in counts.values():
        p = float(count) / total
        if p > 0.0:
            entropy -= p * math.log2(p)

    max_entropy = math.log2(float(len(NodeRole)))
    if max_entropy == 0.0:
        return 0.0
    return entropy / max_entropy


def ctor_ordering_stable(signals: list[NodeSignal]) -> bool:
    if not signals:
        return False
    ordered = sorted(signals, key=lambda s: (s.ctor_slot, s.node_id))
    return all(ordered[i].ctor_slot <= ordered[i + 1].ctor_slot for i in range(len(ordered) - 1))


def vpu_stream_similarity(left: list[float], right: list[float]) -> float:
    if not left and not right:
        return 1.0
    if len(left) != len(right) or not left:
        return 0.0
    left_tuple = tuple(float(v) for v in left)
    right_tuple = tuple(float(v) for v in right)
    return _cosine_similarity(left_tuple, right_tuple)


def cluster_state_score(
    *,
    vpu_density_value: float,
    alignment_coherence_value: float,
    node_entropy_value: float,
    reserve_pressure: float,
) -> float:
    reserve_term = max(0.0, min(1.0, 1.0 - reserve_pressure))
    score = (
        0.35 * max(0.0, min(1.0, vpu_density_value))
        + 0.35 * max(0.0, min(1.0, alignment_coherence_value))
        + 0.20 * max(0.0, min(1.0, 1.0 - node_entropy_value))
        + 0.10 * reserve_term
    )
    return max(0.0, min(1.0, score))
