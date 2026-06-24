from __future__ import annotations

import hashlib
import json


def _canonical_json(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


class ClusterMembership:
    """Tracks role-based node membership within a cluster."""

    SUPPORTED_ROLES = {"VN", "SN", "REN", "LN", "AN", "PTN"}

    def __init__(self):
        self._members: dict[str, dict] = {}

    def register(self, node_id: str, role: str) -> None:
        """Register a node with its role in the cluster.
        
        Raises ValueError if role is unsupported or node_id already registered.
        """
        node_id = str(node_id).strip()
        role = str(role).strip().upper()

        if not node_id:
            raise ValueError("node_id must be non-empty")
        if role not in self.SUPPORTED_ROLES:
            raise ValueError(f"role {role} not in {self.SUPPORTED_ROLES}")
        if node_id in self._members:
            raise ValueError(f"node_id {node_id} already registered")

        self._members[node_id] = {"node_id": node_id, "role": role}

    def snapshot(self) -> list[dict]:
        """Return sorted list of members for deterministic serialization."""
        return sorted(self._members.values(), key=lambda m: m["node_id"])

    def digest(self) -> str:
        """Compute SHA256 digest of canonical membership snapshot."""
        canonical = _canonical_json({"members": self.snapshot()})
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def member_count(self) -> int:
        """Return number of registered members."""
        return len(self._members)


class Cluster:
    """Represents a deterministic cluster with bounded membership."""

    def __init__(self, cluster_id: str):
        cluster_id = str(cluster_id).strip()
        if not cluster_id:
            raise ValueError("cluster_id must be non-empty")
        self._cluster_id = cluster_id
        self._membership = ClusterMembership()
        self._state = {
            "reserve": 0.0,
            "circulation": 0.0,
            "height": 0,
        }

    @property
    def cluster_id(self) -> str:
        return self._cluster_id

    def register_node(self, node_id: str, role: str) -> None:
        """Register a node in this cluster."""
        self._membership.register(node_id, role)

    def snapshot(self) -> dict:
        """Return snapshot of cluster state and membership for deterministic hashing."""
        return {
            "cluster_id": self._cluster_id,
            "members": self._membership.snapshot(),
            "state": {
                "reserve": self._state["reserve"],
                "circulation": self._state["circulation"],
                "height": self._state["height"],
            },
        }

    def cluster_hash(self) -> str:
        """Compute deterministic SHA256 hash of cluster snapshot."""
        canonical = _canonical_json(self.snapshot())
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def cluster_state(self) -> dict:
        """Return immutable copy of cluster state and membership."""
        return {
            "cluster_id": self._cluster_id,
            "members": self._membership.snapshot(),
            "state": dict(self._state),
            "cluster_hash": self.cluster_hash(),
            "membership_digest": self._membership.digest(),
        }

    def member_count(self) -> int:
        """Return number of registered members."""
        return self._membership.member_count()


class ClusterRegistry:
    """Manages multiple deterministic clusters."""

    def __init__(self):
        self._clusters: dict[str, Cluster] = {}

    def create_cluster(self, cluster_id: str) -> Cluster:
        """Create and register a new cluster.
        
        Raises ValueError if cluster_id already exists.
        """
        cluster_id = str(cluster_id).strip()
        if not cluster_id:
            raise ValueError("cluster_id must be non-empty")
        if cluster_id in self._clusters:
            raise ValueError(f"cluster {cluster_id} already exists")

        cluster = Cluster(cluster_id)
        self._clusters[cluster_id] = cluster
        return cluster

    def get_cluster(self, cluster_id: str) -> Cluster | None:
        """Retrieve a cluster by ID."""
        return self._clusters.get(str(cluster_id).strip())

    def snapshot(self) -> list[dict]:
        """Return sorted list of all cluster snapshots for deterministic serialization."""
        snapshots = [self._clusters[cid].snapshot() for cid in sorted(self._clusters.keys())]
        return snapshots

    def registry_digest(self) -> str:
        """Compute SHA256 digest of all clusters for convergence verification."""
        canonical = _canonical_json({"clusters": self.snapshot()})
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def cluster_count(self) -> int:
        """Return number of clusters in registry."""
        return len(self._clusters)

    def total_member_count(self) -> int:
        """Return total nodes across all clusters."""
        return sum(c.member_count() for c in self._clusters.values())

    def registry_state(self) -> dict:
        """Return immutable copy of complete registry state."""
        return {
            "clusters": self.snapshot(),
            "cluster_count": self.cluster_count(),
            "total_members": self.total_member_count(),
            "registry_digest": self.registry_digest(),
        }
