from __future__ import annotations

from .metrics import clamp01


def normalize_vpu_density(vpu_density: float) -> float:
    # Deterministic normalization: vpu_density >= 10 is treated as saturated pressure.
    return clamp01(float(vpu_density) / 10.0)


def compute_demand_pressure(vpu_density: float, alignment_coherence: float, event_intensity: float) -> float:
    vpu_norm = normalize_vpu_density(vpu_density)
    return clamp01(0.50 * vpu_norm + 0.30 * clamp01(alignment_coherence) + 0.20 * clamp01(event_intensity))


def compute_reserve_pressure(reserve_utilization: float, reserve_drift: float) -> float:
    return clamp01(0.70 * clamp01(reserve_utilization) + 0.30 * clamp01(reserve_drift))


def compute_reproduction_pressure(vpu_density: float, ren_share: float, demand_pressure: float) -> float:
    vpu_norm = normalize_vpu_density(vpu_density)
    return clamp01(0.50 * vpu_norm + 0.30 * clamp01(ren_share) + 0.20 * clamp01(demand_pressure))
