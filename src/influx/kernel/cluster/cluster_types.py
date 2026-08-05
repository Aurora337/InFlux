from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class NodeRole(str, Enum):
    VN = "VN"
    SN = "SN"
    REN = "REN"
    PTN = "PTN"


class ClusterType(str, Enum):
    VC = "verification_cluster"
    EC = "economic_cluster"
    PC = "platform_cluster"
    HSC = "hybrid_stability_cluster"


class ClusterLifecycle(str, Enum):
    STABLE = "stable"
    MERGING = "merging"
    SPLITTING = "splitting"
    DECAYING = "decaying"


@dataclass(frozen=True)
class NodeSignal:
    node_id: str
    role: NodeRole
    vpu: float
    alignment_vector: tuple[float, float, float, float]
    ctor_slot: int


@dataclass(frozen=True)
class ClusterThresholds:
    tau_cluster: float = 10.0
    epsilon_alignment_entropy: float = 0.2
    ctor_window_size: int = 8
    merge_alignment_threshold: float = 0.75
    merge_vpu_similarity_threshold: float = 0.8
    split_entropy_max: float = 0.85
    decay_inactivity_windows: int = 3
    decay_min_vpu_density: float = 0.1


@dataclass(frozen=True)
class ClusterState:
    cluster_id: str
    cluster_type: ClusterType
    lifecycle: ClusterLifecycle
    member_nodes: tuple[str, ...]
    ctor_window: tuple[int, int]
    vpu_density: float
    alignment_coherence: float
    alignment_entropy: float
    node_entropy: float
    reserve_pressure: float
    state_score: float
    diagnostics: dict[str, float | int | str] = field(default_factory=dict)
