from __future__ import annotations

from .metrics import ClusterEconomicInput, ClusterMetrics, clamp01
from .pressure import compute_demand_pressure, compute_reproduction_pressure, compute_reserve_pressure
from .stability import compute_stability_index


ROLES = ("VN", "SN", "REN", "PTN", "AN")


def _normalize_role_composition(role_composition: dict[str, float]) -> dict[str, float]:
    base = {role: max(0.0, float(role_composition.get(role, 0.0))) for role in ROLES}
    total = sum(base.values())
    if total <= 0.0:
        equal = 1.0 / float(len(ROLES))
        return {role: equal for role in ROLES}
    return {role: base[role] / total for role in ROLES}


class ClusterEconomicCouplingEngine:
    """Deterministic, observation-only cluster economic coupling calculator."""

    def compute_metrics(self, snapshot: ClusterEconomicInput) -> ClusterMetrics:
        roles = _normalize_role_composition(snapshot.role_composition)

        demand_pressure = compute_demand_pressure(
            vpu_density=snapshot.vpu_density,
            alignment_coherence=snapshot.alignment_coherence,
            event_intensity=snapshot.event_intensity,
        )
        reserve_pressure = compute_reserve_pressure(
            reserve_utilization=snapshot.reserve_utilization,
            reserve_drift=snapshot.reserve_drift,
        )
        reproduction_pressure = compute_reproduction_pressure(
            vpu_density=snapshot.vpu_density,
            ren_share=roles["REN"],
            demand_pressure=demand_pressure,
        )
        stability_index = compute_stability_index(
            alignment_coherence=snapshot.alignment_coherence,
            reserve_pressure=reserve_pressure,
            demand_pressure=demand_pressure,
            reproduction_pressure=reproduction_pressure,
            cluster_entropy=snapshot.cluster_entropy,
        )

        return ClusterMetrics(
            cluster_id=snapshot.cluster_id,
            demand_pressure=demand_pressure,
            reserve_pressure=reserve_pressure,
            reproduction_pressure=reproduction_pressure,
            stability_index=stability_index,
            role_composition_normalized=roles,
        )

    def compute_batch(self, snapshots: list[ClusterEconomicInput]) -> list[ClusterMetrics]:
        # Stable ordering guarantees deterministic outputs across node roles.
        ordered = sorted(snapshots, key=lambda item: item.cluster_id)
        return [self.compute_metrics(item) for item in ordered]


def merge_metric_continuity(
    left: ClusterMetrics,
    right: ClusterMetrics,
    *,
    left_weight: float,
    right_weight: float,
    merged_cluster_id: str,
) -> ClusterMetrics:
    lw = max(0.0, float(left_weight))
    rw = max(0.0, float(right_weight))
    total = lw + rw
    if total <= 0.0:
        lw = rw = 0.5
        total = 1.0

    def _wavg(a: float, b: float) -> float:
        return ((a * lw) + (b * rw)) / total

    roles = {
        role: _wavg(left.role_composition_normalized.get(role, 0.0), right.role_composition_normalized.get(role, 0.0))
        for role in ROLES
    }
    normalized_roles = _normalize_role_composition(roles)

    return ClusterMetrics(
        cluster_id=merged_cluster_id,
        demand_pressure=clamp01(_wavg(left.demand_pressure, right.demand_pressure)),
        reserve_pressure=clamp01(_wavg(left.reserve_pressure, right.reserve_pressure)),
        reproduction_pressure=clamp01(_wavg(left.reproduction_pressure, right.reproduction_pressure)),
        stability_index=clamp01(_wavg(left.stability_index, right.stability_index)),
        role_composition_normalized=normalized_roles,
    )


def split_metric_continuity(
    parent: ClusterMetrics,
    *,
    left_ratio: float,
    left_cluster_id: str,
    right_cluster_id: str,
) -> tuple[ClusterMetrics, ClusterMetrics]:
    ratio = clamp01(left_ratio)

    left_roles = dict(parent.role_composition_normalized)
    right_roles = dict(parent.role_composition_normalized)

    left = ClusterMetrics(
        cluster_id=left_cluster_id,
        demand_pressure=parent.demand_pressure,
        reserve_pressure=parent.reserve_pressure,
        reproduction_pressure=parent.reproduction_pressure,
        stability_index=parent.stability_index,
        role_composition_normalized=left_roles,
    )
    right = ClusterMetrics(
        cluster_id=right_cluster_id,
        demand_pressure=parent.demand_pressure,
        reserve_pressure=parent.reserve_pressure,
        reproduction_pressure=parent.reproduction_pressure,
        stability_index=parent.stability_index,
        role_composition_normalized=right_roles,
    )

    # Deterministic continuity scalar for downstream accounting (not state mutation).
    _ = ratio
    return left, right
