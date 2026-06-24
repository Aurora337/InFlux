from __future__ import annotations

from dataclasses import dataclass

from .cluster_engine import ClusterDetectionEngine
from .cluster_equations import ctor_ordering_stable
from .cluster_types import ClusterThresholds, NodeRole, NodeSignal


@dataclass(frozen=True)
class ClusterEvent:
    event_id: str
    node_id: str
    role: NodeRole
    vpu: float
    alignment_vector: tuple[float, float, float, float]
    ctor_slot: int
    reserve_pressure: float = 0.0


def default_event_stream() -> list[ClusterEvent]:
    return [
        ClusterEvent("e-001", "vn-1", NodeRole.VN, 6.0, (0.9, 0.9, 0.9, 0.9), 0, 0.1),
        ClusterEvent("e-002", "vn-2", NodeRole.VN, 5.0, (0.88, 0.9, 0.9, 0.9), 1, 0.1),
        ClusterEvent("e-003", "ren-1", NodeRole.REN, 6.0, (0.87, 0.9, 0.9, 0.9), 2, 0.2),
        ClusterEvent("e-004", "ren-2", NodeRole.REN, 5.0, (0.86, 0.9, 0.9, 0.9), 3, 0.2),
        ClusterEvent("e-005", "ptn-1", NodeRole.PTN, 6.0, (0.91, 0.9, 0.9, 0.9), 8, 0.15),
        ClusterEvent("e-006", "ptn-2", NodeRole.PTN, 5.0, (0.9, 0.88, 0.9, 0.9), 9, 0.15),
        ClusterEvent("e-007", "sn-1", NodeRole.SN, 6.0, (0.9, 0.9, 0.88, 0.9), 10, 0.2),
        ClusterEvent("e-008", "sn-2", NodeRole.SN, 5.0, (0.9, 0.9, 0.9, 0.88), 11, 0.2),
    ]


def _window_index(ctor_slot: int, size: int) -> int:
    return ctor_slot // max(1, size)


def _event_to_signal(event: ClusterEvent) -> NodeSignal:
    return NodeSignal(
        node_id=event.node_id,
        role=event.role,
        vpu=event.vpu,
        alignment_vector=event.alignment_vector,
        ctor_slot=event.ctor_slot,
    )


def _as_dict(event: ClusterEvent) -> dict:
    return {
        "event_id": event.event_id,
        "node_id": event.node_id,
        "role": event.role.value,
        "vpu": event.vpu,
        "alignment_vector": list(event.alignment_vector),
        "ctor_slot": event.ctor_slot,
        "reserve_pressure": event.reserve_pressure,
    }


def run_cluster_emergence_simulation(
    events: list[ClusterEvent],
    *,
    thresholds: ClusterThresholds | None = None,
) -> dict:
    cfg = thresholds or ClusterThresholds()
    engine = ClusterDetectionEngine(thresholds=cfg)

    ordered_events = sorted(events, key=lambda e: (e.ctor_slot, e.node_id, e.event_id))
    if not ordered_events:
        return {
            "suite": "v1.3.7-cluster-emergence-simulation",
            "event_count": 0,
            "window_count": 0,
            "simulation_valid": True,
            "windows": [],
        }

    min_window = _window_index(ordered_events[0].ctor_slot, cfg.ctor_window_size)
    max_window = _window_index(ordered_events[-1].ctor_slot, cfg.ctor_window_size)

    windows: list[dict] = []
    inactivity_windows = 0

    for window in range(min_window, max_window + 1):
        in_window = [
            event
            for event in ordered_events
            if _window_index(event.ctor_slot, cfg.ctor_window_size) == window
        ]
        signals = [_event_to_signal(event) for event in in_window]

        if in_window:
            inactivity_windows = 0
        else:
            inactivity_windows += 1

        reserve_pressure = (
            sum(event.reserve_pressure for event in in_window) / float(len(in_window))
            if in_window
            else 0.0
        )
        ren_activity_cycles = sum(1 for event in in_window if event.role == NodeRole.REN and event.vpu > 0.0)

        formed = engine.form_clusters(
            signals,
            reserve_pressure=reserve_pressure,
            inactivity_windows=inactivity_windows,
            ren_activity_cycles=ren_activity_cycles,
        )
        transitioned = engine.evaluate_transitions(formed, ctor_stable=ctor_ordering_stable(signals))

        windows.append(
            {
                "window_index": window,
                "event_count": len(in_window),
                "ctor_stable": ctor_ordering_stable(signals),
                "reserve_pressure": reserve_pressure,
                "ren_activity_cycles": ren_activity_cycles,
                "events": [_as_dict(event) for event in in_window],
                "clusters": [
                    {
                        "cluster_id": cluster.cluster_id,
                        "cluster_type": cluster.cluster_type.value,
                        "lifecycle": cluster.lifecycle.value,
                        "member_nodes": list(cluster.member_nodes),
                        "ctor_window": list(cluster.ctor_window),
                        "vpu_density": cluster.vpu_density,
                        "alignment_coherence": cluster.alignment_coherence,
                        "alignment_entropy": cluster.alignment_entropy,
                        "node_entropy": cluster.node_entropy,
                        "reserve_pressure": cluster.reserve_pressure,
                        "state_score": cluster.state_score,
                    }
                    for cluster in transitioned
                ],
            }
        )

    lifecycle_count: dict[str, int] = {}
    type_count: dict[str, int] = {}
    for window in windows:
        for cluster in window["clusters"]:
            lifecycle_count[cluster["lifecycle"]] = lifecycle_count.get(cluster["lifecycle"], 0) + 1
            type_count[cluster["cluster_type"]] = type_count.get(cluster["cluster_type"], 0) + 1

    return {
        "suite": "v1.3.7-cluster-emergence-simulation",
        "event_count": len(ordered_events),
        "window_count": len(windows),
        "simulation_valid": True,
        "thresholds": {
            "tau_cluster": cfg.tau_cluster,
            "epsilon_alignment_entropy": cfg.epsilon_alignment_entropy,
            "ctor_window_size": cfg.ctor_window_size,
            "merge_alignment_threshold": cfg.merge_alignment_threshold,
            "merge_vpu_similarity_threshold": cfg.merge_vpu_similarity_threshold,
            "split_entropy_max": cfg.split_entropy_max,
            "decay_inactivity_windows": cfg.decay_inactivity_windows,
            "decay_min_vpu_density": cfg.decay_min_vpu_density,
        },
        "lifecycle_counts": lifecycle_count,
        "cluster_type_counts": type_count,
        "windows": windows,
    }
