from __future__ import annotations

import hashlib
import json
from typing import Optional


def _canonical_json(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


class ClusterStateExchange:
    """Represents state exchanged between two clusters during synchronization."""

    def __init__(self, cluster_id: str, state_snapshot: dict, cluster_hash: str):
        """Initialize state exchange from a cluster.
        
        Args:
            cluster_id: Identifier of the cluster exporting state
            state_snapshot: Canonical snapshot of cluster state (members, ledger, economic)
            cluster_hash: Deterministic hash of the cluster
        """
        self.cluster_id = str(cluster_id).strip()
        self.state_snapshot = dict(state_snapshot)
        self.cluster_hash = str(cluster_hash).strip()

        if not self.cluster_id:
            raise ValueError("cluster_id must be non-empty")
        if not self.cluster_hash:
            raise ValueError("cluster_hash must be non-empty")

    def exchange_digest(self) -> str:
        """Compute deterministic digest of exchange payload."""
        payload = {
            "cluster_id": self.cluster_id,
            "state_snapshot": self.state_snapshot,
            "cluster_hash": self.cluster_hash,
        }
        canonical = _canonical_json(payload)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class SynchronizationSession:
    """Manages state synchronization between two clusters."""

    def __init__(self, cluster_a_id: str, cluster_b_id: str):
        """Initialize synchronization session between two clusters.
        
        Args:
            cluster_a_id: ID of first cluster
            cluster_b_id: ID of second cluster
        """
        self.cluster_a_id = str(cluster_a_id).strip()
        self.cluster_b_id = str(cluster_b_id).strip()
        
        if not self.cluster_a_id or not self.cluster_b_id:
            raise ValueError("cluster IDs must be non-empty")
        
        self._exchange_a_to_b: Optional[ClusterStateExchange] = None
        self._exchange_b_to_a: Optional[ClusterStateExchange] = None
        self._converged = False
        self._convergence_hash: Optional[str] = None

    def exchange_state(
        self,
        from_cluster_id: str,
        state_snapshot: dict,
        cluster_hash: str,
    ) -> None:
        """Receive state exchange from one cluster.
        
        Args:
            from_cluster_id: ID of cluster sending state
            state_snapshot: Canonical state snapshot
            cluster_hash: Deterministic cluster hash
            
        Raises:
            ValueError if cluster_id is not part of this session
        """
        from_cluster_id = str(from_cluster_id).strip()
        
        if from_cluster_id == self.cluster_a_id:
            self._exchange_a_to_b = ClusterStateExchange(
                from_cluster_id,
                state_snapshot,
                cluster_hash,
            )
        elif from_cluster_id == self.cluster_b_id:
            self._exchange_b_to_a = ClusterStateExchange(
                from_cluster_id,
                state_snapshot,
                cluster_hash,
            )
        else:
            raise ValueError(
                f"cluster_id {from_cluster_id} not in session "
                f"({self.cluster_a_id}, {self.cluster_b_id})"
            )

    def compare_hashes(self) -> dict:
        """Compare hashes of both exchanges.
        
        Returns dict with:
        - hash_a: hash from cluster A
        - hash_b: hash from cluster B
        - hashes_match: True if both hashes are identical
        """
        if not self._exchange_a_to_b or not self._exchange_b_to_a:
            return {
                "hash_a": None,
                "hash_b": None,
                "hashes_match": False,
                "complete": False,
            }
        
        hash_a = self._exchange_a_to_b.cluster_hash
        hash_b = self._exchange_b_to_a.cluster_hash
        
        return {
            "hash_a": hash_a,
            "hash_b": hash_b,
            "hashes_match": hash_a == hash_b,
            "complete": True,
        }

    def synchronize(self) -> bool:
        """Perform synchronization and verify convergence.
        
        Returns True if both clusters have converged to identical state.
        """
        comparison = self.compare_hashes()
        
        if not comparison["complete"]:
            self._converged = False
            return False
        
        if comparison["hashes_match"]:
            self._converged = True
            self._convergence_hash = comparison["hash_a"]
            return True
        
        self._converged = False
        return False

    def verify_convergence(self) -> dict:
        """Verify that synchronization resulted in convergence.
        
        Returns dict with convergence details.
        """
        comparison = self.compare_hashes()
        
        return {
            "converged": self._converged,
            "convergence_hash": self._convergence_hash,
            "cluster_a_hash": comparison["hash_a"],
            "cluster_b_hash": comparison["hash_b"],
            "hashes_match": comparison["hashes_match"],
            "session_complete": comparison["complete"],
        }

    def session_digest(self) -> str:
        """Compute deterministic digest of entire session for verification."""
        payload = {
            "cluster_a_id": self.cluster_a_id,
            "cluster_b_id": self.cluster_b_id,
            "converged": self._converged,
            "convergence_hash": self._convergence_hash,
        }
        canonical = _canonical_json(payload)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class SynchronizationResult:
    """Represents the result of a synchronization session."""

    def __init__(self):
        self.sessions: list[dict] = []
        self._result_hash: Optional[str] = None

    def add_session_result(self, session: SynchronizationSession) -> None:
        """Record result from a synchronization session.
        
        Args:
            session: Completed SynchronizationSession
        """
        verification = session.verify_convergence()
        self.sessions.append({
            "cluster_a": session.cluster_a_id,
            "cluster_b": session.cluster_b_id,
            "converged": verification["converged"],
            "convergence_hash": verification["convergence_hash"],
            "hashes_match": verification["hashes_match"],
        })

    def all_converged(self) -> bool:
        """Check if all sessions resulted in convergence."""
        return all(s["converged"] for s in self.sessions)

    def convergence_hash_match(self) -> bool:
        """Check if all sessions converged to the same hash."""
        if not self.sessions:
            return False
        if not self.all_converged():
            return False
        
        convergence_hashes = {
            s["convergence_hash"]
            for s in self.sessions
            if s["convergence_hash"]
        }
        
        return len(convergence_hashes) == 1

    def result_summary(self) -> dict:
        """Return deterministic summary of synchronization result."""
        return {
            "sessions_completed": len(self.sessions),
            "all_converged": self.all_converged(),
            "convergence_hash_match": self.convergence_hash_match(),
            "sessions": sorted(
                self.sessions,
                key=lambda s: (s["cluster_a"], s["cluster_b"]),
            ),
        }

    def result_digest(self) -> str:
        """Compute deterministic digest of result for verification."""
        canonical = _canonical_json(self.result_summary())
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
