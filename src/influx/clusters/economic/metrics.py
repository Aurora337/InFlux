from __future__ import annotations

from dataclasses import dataclass


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True)
class ClusterEconomicInput:
    cluster_id: str
    vpu_density: float
    alignment_coherence: float
    event_intensity: float
    reserve_utilization: float
    reserve_drift: float
    cluster_entropy: float
    role_composition: dict[str, float]


@dataclass(frozen=True)
class ClusterMetrics:
    cluster_id: str
    demand_pressure: float
    reserve_pressure: float
    reproduction_pressure: float
    stability_index: float
    role_composition_normalized: dict[str, float]
