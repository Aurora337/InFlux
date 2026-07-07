from __future__ import annotations

import hashlib
from itertools import combinations

from .cluster_equations import (
    alignment_coherence,
    alignment_entropy,
    cluster_state_score,
    ctor_ordering_stable,
    node_entropy,
    vpu_density,
)
from .cluster_types import (
    ClusterLifecycle,
    ClusterState,
    ClusterThresholds,
    ClusterType,
    NodeRole,
    NodeSignal,
)
from .decay_rules import should_decay
from .genesis_rules import classify_cluster_type, cluster_genesis_valid
from .merge_split_rules import can_merge, deterministic_split_nodes, must_split


class ClusterDetectionEngine:
    """Deterministic engine for cluster formation and transition evaluation."""

    def __init__(self, thresholds: ClusterThresholds | None = None):
        self.thresholds = thresholds or ClusterThresholds()

    def form_clusters(
        self,
        signals: list[NodeSignal],
        *,
        reserve_pressure: float = 0.0,
        inactivity_windows: int = 0,
        ren_activity_cycles: int = 1,
    ) -> list[ClusterState]:
        if not signals:
            return []

        buckets = self._partition_signals(signals)
        clusters: list[ClusterState] = []

        for key in sorted(buckets.keys()):
            group = buckets[key]
            if not cluster_genesis_valid(group, self.thresholds):
                continue

            lifecycle = ClusterLifecycle.STABLE
            group_vpu_density = vpu_density(group)
            if should_decay(
                inactivity_windows=inactivity_windows,
                ren_activity_cycles=ren_activity_cycles,
                vpu_density=group_vpu_density,
                thresholds=self.thresholds,
            ):
                lifecycle = ClusterLifecycle.DECAYING

            clusters.append(
                self._build_state(
                    signals=group,
                    cluster_type=classify_cluster_type(group),
                    lifecycle=lifecycle,
                    reserve_pressure=reserve_pressure,
                )
            )

        return sorted(clusters, key=lambda c: c.cluster_id)

    def evaluate_transitions(
        self,
        clusters: list[ClusterState],
        *,
        ctor_stable: bool = True,
    ) -> list[ClusterState]:
        if not clusters:
            return []

        updated = {cluster.cluster_id: cluster for cluster in clusters}

        for left, right in combinations(sorted(clusters, key=lambda c: c.cluster_id), 2):
            if can_merge(left, right, self.thresholds):
                merged = self._merge_state(left, right)
                updated[left.cluster_id] = merged
                updated[right.cluster_id] = merged

        results: list[ClusterState] = []
        for cluster in sorted(updated.values(), key=lambda c: c.cluster_id):
            if must_split(cluster, self.thresholds, ctor_stable=ctor_stable):
                left_nodes, right_nodes = deterministic_split_nodes(cluster.member_nodes)
                split_nodes = left_nodes if left_nodes else cluster.member_nodes
                results.append(
                    ClusterState(
                        cluster_id=cluster.cluster_id,
                        cluster_type=cluster.cluster_type,
                        lifecycle=ClusterLifecycle.SPLITTING,
                        member_nodes=split_nodes,
                        ctor_window=cluster.ctor_window,
                        vpu_density=cluster.vpu_density,
                        alignment_coherence=cluster.alignment_coherence,
                        alignment_entropy=cluster.alignment_entropy,
                        node_entropy=cluster.node_entropy,
                        reserve_pressure=cluster.reserve_pressure,
                        state_score=cluster.state_score,
                        diagnostics=dict(cluster.diagnostics),
                    )
                )
                continue
            results.append(cluster)

        dedup = {cluster.cluster_id: cluster for cluster in results}
        return sorted(dedup.values(), key=lambda c: c.cluster_id)

    def _partition_signals(self, signals: list[NodeSignal]) -> dict[tuple[int, NodeRole], list[NodeSignal]]:
        ordered = sorted(signals, key=lambda s: (s.ctor_slot, s.node_id))
        buckets: dict[tuple[int, NodeRole], list[NodeSignal]] = {}
        for signal in ordered:
            window = signal.ctor_slot // max(1, self.thresholds.ctor_window_size)
            key = (window, signal.role)
            buckets.setdefault(key, []).append(signal)
        return buckets

    def _build_state(
        self,
        *,
        signals: list[NodeSignal],
        cluster_type: ClusterType,
        lifecycle: ClusterLifecycle,
        reserve_pressure: float,
    ) -> ClusterState:
        ordered = sorted(signals, key=lambda s: (s.ctor_slot, s.node_id))
        member_nodes = tuple(signal.node_id for signal in ordered)
        ctor_slots = [signal.ctor_slot for signal in ordered]
        window = (min(ctor_slots), max(ctor_slots))

        vpu_value = vpu_density(ordered)
        coherence_value = alignment_coherence(ordered)
        entropy_value = alignment_entropy(ordered)
        node_entropy_value = node_entropy(ordered)

        cluster_id_seed = "|".join(
            [
                cluster_type.value,
                ",".join(member_nodes),
                str(window[0]),
                str(window[1]),
            ]
        )
        cluster_id = hashlib.sha256(cluster_id_seed.encode("utf-8")).hexdigest()[:16]

        return ClusterState(
            cluster_id=cluster_id,
            cluster_type=cluster_type,
            lifecycle=lifecycle,
            member_nodes=member_nodes,
            ctor_window=window,
            vpu_density=vpu_value,
            alignment_coherence=coherence_value,
            alignment_entropy=entropy_value,
            node_entropy=node_entropy_value,
            reserve_pressure=reserve_pressure,
            state_score=cluster_state_score(
                vpu_density_value=vpu_value,
                alignment_coherence_value=coherence_value,
                node_entropy_value=node_entropy_value,
                reserve_pressure=reserve_pressure,
            ),
            diagnostics={
                "signal_count": len(ordered),
                "ctor_stable": int(ctor_ordering_stable(ordered)),
            },
        )

    def _merge_state(self, left: ClusterState, right: ClusterState) -> ClusterState:
        member_nodes = tuple(sorted(set(left.member_nodes + right.member_nodes)))
        window = (
            min(left.ctor_window[0], right.ctor_window[0]),
            max(left.ctor_window[1], right.ctor_window[1]),
        )

        merged_seed = "|".join([left.cluster_id, right.cluster_id, ",".join(member_nodes)])
        cluster_id = hashlib.sha256(merged_seed.encode("utf-8")).hexdigest()[:16]

        return ClusterState(
            cluster_id=cluster_id,
            cluster_type=ClusterType.HSC,
            lifecycle=ClusterLifecycle.MERGING,
            member_nodes=member_nodes,
            ctor_window=window,
            vpu_density=(left.vpu_density + right.vpu_density) / 2.0,
            alignment_coherence=min(left.alignment_coherence, right.alignment_coherence),
            alignment_entropy=max(left.alignment_entropy, right.alignment_entropy),
            node_entropy=max(left.node_entropy, right.node_entropy),
            reserve_pressure=max(left.reserve_pressure, right.reserve_pressure),
            state_score=(left.state_score + right.state_score) / 2.0,
            diagnostics={"merged_from": 2},
        )
