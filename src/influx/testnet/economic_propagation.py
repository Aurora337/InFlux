"""Economic propagation protocol for cluster network synchronization.

Extends cross-cluster synchronization to include economic state propagation.
Three clusters with identical economic state deterministically converge on identical
economic view through pairwise synchronization sessions.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class EconomicStateExchange:
    """Encapsulates economic state exported from one cluster for synchronization."""

    cluster_id: str
    reserve_supply: float
    circulating_supply: float
    economic_epoch: int
    cluster_metrics: dict  # {demand_pressure, reserve_pressure, reproduction_pressure, stability_index}

    def exchange_digest(self) -> str:
        """Compute deterministic SHA256 digest of economic state.

        Returns:
            64-char hex string representing canonical state hash.
        """
        canonical = json.dumps(
            {
                "cluster_id": self.cluster_id,
                "reserve_supply": self.reserve_supply,
                "circulating_supply": self.circulating_supply,
                "economic_epoch": self.economic_epoch,
                "cluster_metrics": self.cluster_metrics,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode()).hexdigest()


@dataclass
class EconomicSyncSession:
    """Manages bidirectional economic state exchange between two clusters."""

    cluster_a_id: str
    cluster_b_id: str
    _state_a: EconomicStateExchange | None = None
    _state_b: EconomicStateExchange | None = None
    _converged: bool = False
    _convergence_hash: str | None = None

    def exchange_state(
        self, cluster_id: str, state: EconomicStateExchange
    ) -> None:
        """Accept economic state from either cluster.

        Args:
            cluster_id: Identifier of cluster providing state
            state: EconomicStateExchange from cluster

        Raises:
            ValueError: If cluster_id not recognized in this session
        """
        if cluster_id == self.cluster_a_id:
            self._state_a = state
        elif cluster_id == self.cluster_b_id:
            self._state_b = state
        else:
            raise ValueError(
                f"Cluster {cluster_id} not in session "
                f"({self.cluster_a_id}, {self.cluster_b_id})"
            )

    def compare_hashes(self) -> dict:
        """Compare economic state hashes from both clusters.

        Returns:
            Dict with keys: hash_a, hash_b, match (bool)

        Raises:
            RuntimeError: If either state not yet exchanged
        """
        if self._state_a is None or self._state_b is None:
            raise RuntimeError("Both clusters must exchange state before comparison")

        hash_a = self._state_a.exchange_digest()
        hash_b = self._state_b.exchange_digest()
        return {"hash_a": hash_a, "hash_b": hash_b, "match": hash_a == hash_b}

    def synchronize(self) -> bool:
        """Perform economic convergence between clusters.

        Validates that both clusters have exchanged state and computes
        convergence hash.

        Returns:
            True if clusters converged to same economic state

        Raises:
            RuntimeError: If either state not yet exchanged
        """
        if self._state_a is None or self._state_b is None:
            raise RuntimeError("Both clusters must exchange state before synchronization")

        # Both states converge if they produce identical hashes
        comparison = self.compare_hashes()
        self._converged = comparison["match"]

        if self._converged:
            # Use canonical convergence hash
            self._convergence_hash = self._state_a.exchange_digest()

        return self._converged

    def verify_convergence(self) -> dict:
        """Verify economic convergence details.

        Returns:
            Dict with keys: converged (bool), convergence_hash (str or None),
            state_a_hash, state_b_hash, reserve_match, epoch_match, metrics_match
        """
        if self._state_a is None or self._state_b is None:
            raise RuntimeError("Both clusters must exchange state before verification")

        hash_a = self._state_a.exchange_digest()
        hash_b = self._state_b.exchange_digest()
        reserve_match = (
            self._state_a.reserve_supply == self._state_b.reserve_supply
        )
        epoch_match = (
            self._state_a.economic_epoch == self._state_b.economic_epoch
        )
        metrics_match = (
            self._state_a.cluster_metrics == self._state_b.cluster_metrics
        )

        return {
            "converged": self._converged,
            "convergence_hash": self._convergence_hash,
            "state_a_hash": hash_a,
            "state_b_hash": hash_b,
            "reserve_match": reserve_match,
            "epoch_match": epoch_match,
            "metrics_match": metrics_match,
        }

    def session_digest(self) -> str:
        """Compute deterministic session hash.

        Returns:
            64-char hex string representing canonical session hash.
        """
        canonical = json.dumps(
            {
                "cluster_a": self.cluster_a_id,
                "cluster_b": self.cluster_b_id,
                "converged": self._converged,
                "convergence_hash": self._convergence_hash,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode()).hexdigest()


@dataclass
class EconomicPropagationResult:
    """Aggregates multiple economic synchronization sessions."""

    _sessions: dict[str, EconomicSyncSession] = None

    def __post_init__(self):
        if self._sessions is None:
            self._sessions = {}

    def add_session_result(self, session_id: str, session: EconomicSyncSession) -> None:
        """Record economic synchronization session result.

        Args:
            session_id: Unique identifier for this session
            session: Completed EconomicSyncSession
        """
        self._sessions[session_id] = session

    def all_converged(self) -> bool:
        """Check if all sessions converged.

        Returns:
            True if all recorded sessions show economic convergence
        """
        if not self._sessions:
            return False
        return all(session._converged for session in self._sessions.values())

    def convergence_hash_match(self) -> bool:
        """Verify all sessions converged to same economic hash.

        Returns:
            True if all sessions have identical convergence hashes

        Raises:
            RuntimeError: If no converged sessions exist
        """
        converged_sessions = [
            s for s in self._sessions.values() if s._converged
        ]
        if not converged_sessions:
            raise RuntimeError("No converged sessions to compare")

        convergence_hashes = [
            s._convergence_hash for s in converged_sessions
        ]
        return len(set(convergence_hashes)) == 1

    def result_summary(self) -> list[dict]:
        """Get sorted session details.

        Returns:
            List of session summaries sorted by cluster pair
        """
        summaries = []
        for session_id in sorted(self._sessions.keys()):
            session = self._sessions[session_id]
            summaries.append(
                {
                    "cluster_a": session.cluster_a_id,
                    "cluster_b": session.cluster_b_id,
                    "converged": session._converged,
                    "convergence_hash": session._convergence_hash,
                    "hashes_match": session.compare_hashes()["match"],
                }
            )
        return summaries

    def result_digest(self) -> str:
        """Compute deterministic result verification hash.

        Returns:
            64-char hex string representing canonical result hash.
        """
        canonical = json.dumps(
            {
                "sessions": len(self._sessions),
                "all_converged": self.all_converged(),
                "convergence_hash_match": (
                    self.convergence_hash_match()
                    if self.all_converged()
                    else False
                ),
                "session_summary": self.result_summary(),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode()).hexdigest()
