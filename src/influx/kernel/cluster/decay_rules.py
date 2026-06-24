from __future__ import annotations

from .cluster_types import ClusterThresholds


def should_decay(
    *,
    inactivity_windows: int,
    ren_activity_cycles: int,
    vpu_density: float,
    thresholds: ClusterThresholds,
) -> bool:
    if inactivity_windows >= thresholds.decay_inactivity_windows:
        return True
    return ren_activity_cycles == 0 and vpu_density <= thresholds.decay_min_vpu_density
