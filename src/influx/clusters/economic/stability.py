from __future__ import annotations

from .metrics import clamp01


def compute_stability_index(
    alignment_coherence: float,
    reserve_pressure: float,
    demand_pressure: float,
    reproduction_pressure: float,
    cluster_entropy: float,
) -> float:
    balance_term = 1.0 - abs(clamp01(demand_pressure) - clamp01(reproduction_pressure))
    score = (
        0.40 * clamp01(alignment_coherence)
        + 0.25 * (1.0 - clamp01(reserve_pressure))
        + 0.20 * clamp01(balance_term)
        + 0.15 * (1.0 - clamp01(cluster_entropy))
    )
    return clamp01(score)
