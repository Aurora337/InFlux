"""Golden tests for economic propagation protocol.

Validates deterministic economic state propagation, convergence, and verification
across multi-cluster network.
"""

import pytest
from src.influx.testnet.economic_propagation import (
    EconomicStateExchange,
    EconomicSyncSession,
    EconomicPropagationResult,
)


def _create_economic_state(cluster_id: str, epoch: int = 1) -> EconomicStateExchange:
    """Helper: Create deterministic economic state."""
    return EconomicStateExchange(
        cluster_id=cluster_id,
        reserve_supply=500.0,
        circulating_supply=1000.0,
        economic_epoch=epoch,
        cluster_metrics={
            "demand_pressure": 0.45,
            "reserve_pressure": 0.30,
            "reproduction_pressure": 0.50,
            "stability_index": 0.72,
        },
    )


class TestEconomicStateExchange:
    """Test EconomicStateExchange behavior."""

    def test_economic_state_exchange_creation(self):
        """Validate economic state exchange initialization."""
        state = _create_economic_state("cluster-econ-001")
        assert state.cluster_id == "cluster-econ-001"
        assert state.reserve_supply == 500.0
        assert state.circulating_supply == 1000.0
        assert state.economic_epoch == 1

    def test_exchange_digest_deterministic(self):
        """Verify exchange digest is deterministic and stable."""
        state1 = _create_economic_state("cluster-econ-001", epoch=1)
        state2 = _create_economic_state("cluster-econ-001", epoch=1)

        digest1 = state1.exchange_digest()
        digest2 = state2.exchange_digest()

        assert digest1 == digest2
        assert len(digest1) == 64  # SHA256 hex


class TestEconomicSyncSession:
    """Test EconomicSyncSession behavior."""

    def test_economic_sync_session_creation(self):
        """Validate economic sync session initialization."""
        session = EconomicSyncSession(
            cluster_a_id="cluster-econ-001",
            cluster_b_id="cluster-econ-002",
        )
        assert session.cluster_a_id == "cluster-econ-001"
        assert session.cluster_b_id == "cluster-econ-002"
        assert session._converged is False

    def test_exchange_state_bidirectional(self):
        """Verify economic state can be exchanged in both directions."""
        session = EconomicSyncSession(
            cluster_a_id="cluster-econ-001",
            cluster_b_id="cluster-econ-002",
        )
        state_a = _create_economic_state("cluster-econ-001")
        state_b = _create_economic_state("cluster-econ-002")

        session.exchange_state("cluster-econ-001", state_a)
        session.exchange_state("cluster-econ-002", state_b)

        assert session._state_a is not None
        assert session._state_b is not None

    def test_exchange_state_invalid_cluster_raises(self):
        """Confirm ValueError for unknown cluster_id."""
        session = EconomicSyncSession(
            cluster_a_id="cluster-econ-001",
            cluster_b_id="cluster-econ-002",
        )
        state = _create_economic_state("cluster-econ-999")

        with pytest.raises(ValueError, match="not in session"):
            session.exchange_state("cluster-econ-999", state)

    def test_identical_economic_states_converge(self):
        """Test convergence when clusters have identical economic state."""
        session = EconomicSyncSession(
            cluster_a_id="cluster-econ-001",
            cluster_b_id="cluster-econ-002",
        )

        # Both clusters with same economic state (matching reserve, supply, epoch, metrics)
        state_a = EconomicStateExchange(
            cluster_id="cluster-econ-001",
            reserve_supply=500.0,
            circulating_supply=1000.0,
            economic_epoch=1,
            cluster_metrics={
                "demand_pressure": 0.45,
                "reserve_pressure": 0.30,
                "reproduction_pressure": 0.50,
                "stability_index": 0.72,
            },
        )
        state_b = EconomicStateExchange(
            cluster_id="cluster-econ-002",
            reserve_supply=500.0,
            circulating_supply=1000.0,
            economic_epoch=1,
            cluster_metrics={
                "demand_pressure": 0.45,
                "reserve_pressure": 0.30,
                "reproduction_pressure": 0.50,
                "stability_index": 0.72,
            },
        )

        session.exchange_state("cluster-econ-001", state_a)
        session.exchange_state("cluster-econ-002", state_b)

        converged = session.synchronize()
        assert converged is True
        assert session._convergence_hash is not None
        assert len(session._convergence_hash) == 64


class TestEconomicPropagationResult:
    """Test EconomicPropagationResult behavior."""

    def test_economic_propagation_result_creation(self):
        """Validate result aggregation initialization."""
        result = EconomicPropagationResult()
        assert result._sessions == {}

    def test_add_session_and_check_convergence(self):
        """Test adding economic sessions and checking convergence."""
        result = EconomicPropagationResult()
        session = EconomicSyncSession(
            cluster_a_id="cluster-econ-001",
            cluster_b_id="cluster-econ-002",
        )

        state_a = _create_economic_state("cluster-econ-001")
        state_b = _create_economic_state("cluster-econ-002")

        session.exchange_state("cluster-econ-001", state_a)
        session.exchange_state("cluster-econ-002", state_b)
        session.synchronize()

        result.add_session_result("session-1", session)

        assert result.all_converged() is True
        assert result.convergence_hash_match() is True

    def test_three_cluster_economic_convergence(self):
        """Full scenario: three clusters converge economically."""
        result = EconomicPropagationResult()

        # Three pairwise sessions with identical economic state
        state_1 = EconomicStateExchange(
            cluster_id="instance-1",
            reserve_supply=500.0,
            circulating_supply=1000.0,
            economic_epoch=42,
            cluster_metrics={
                "demand_pressure": 0.45,
                "reserve_pressure": 0.30,
                "reproduction_pressure": 0.50,
                "stability_index": 0.72,
            },
        )
        state_2 = EconomicStateExchange(
            cluster_id="instance-2",
            reserve_supply=500.0,
            circulating_supply=1000.0,
            economic_epoch=42,
            cluster_metrics={
                "demand_pressure": 0.45,
                "reserve_pressure": 0.30,
                "reproduction_pressure": 0.50,
                "stability_index": 0.72,
            },
        )
        state_3 = EconomicStateExchange(
            cluster_id="instance-3",
            reserve_supply=500.0,
            circulating_supply=1000.0,
            economic_epoch=42,
            cluster_metrics={
                "demand_pressure": 0.45,
                "reserve_pressure": 0.30,
                "reproduction_pressure": 0.50,
                "stability_index": 0.72,
            },
        )

        # Session 1-2
        session_1_2 = EconomicSyncSession(
            cluster_a_id="instance-1",
            cluster_b_id="instance-2",
        )
        session_1_2.exchange_state("instance-1", state_1)
        session_1_2.exchange_state("instance-2", state_2)
        session_1_2.synchronize()
        result.add_session_result("session-1-2", session_1_2)

        # Session 2-3
        session_2_3 = EconomicSyncSession(
            cluster_a_id="instance-2",
            cluster_b_id="instance-3",
        )
        session_2_3.exchange_state("instance-2", state_2)
        session_2_3.exchange_state("instance-3", state_3)
        session_2_3.synchronize()
        result.add_session_result("session-2-3", session_2_3)

        # Session 1-3
        session_1_3 = EconomicSyncSession(
            cluster_a_id="instance-1",
            cluster_b_id="instance-3",
        )
        session_1_3.exchange_state("instance-1", state_1)
        session_1_3.exchange_state("instance-3", state_3)
        session_1_3.synchronize()
        result.add_session_result("session-1-3", session_1_3)

        # All converged and same hash
        assert result.all_converged() is True
        assert result.convergence_hash_match() is True
        summary = result.result_summary()
        assert len(summary) == 3
        assert all(item["converged"] for item in summary)


class TestEconomicPropagationDeterminism:
    """Test determinism and order-independence of economic propagation."""

    def test_economic_propagation_is_deterministic(self):
        """Identical sessions produce identical digests."""
        session_1 = EconomicSyncSession(
            cluster_a_id="cluster-econ-001",
            cluster_b_id="cluster-econ-002",
        )
        state_a1 = _create_economic_state("cluster-econ-001")
        state_b1 = _create_economic_state("cluster-econ-002")
        session_1.exchange_state("cluster-econ-001", state_a1)
        session_1.exchange_state("cluster-econ-002", state_b1)
        session_1.synchronize()
        digest_1 = session_1.session_digest()

        session_2 = EconomicSyncSession(
            cluster_a_id="cluster-econ-001",
            cluster_b_id="cluster-econ-002",
        )
        state_a2 = _create_economic_state("cluster-econ-001")
        state_b2 = _create_economic_state("cluster-econ-002")
        session_2.exchange_state("cluster-econ-001", state_a2)
        session_2.exchange_state("cluster-econ-002", state_b2)
        session_2.synchronize()
        digest_2 = session_2.session_digest()

        assert digest_1 == digest_2
        assert len(digest_1) == 64

    def test_economic_propagation_order_independence(self):
        """Exchange order doesn't affect comparison results."""
        # Forward: A->B then B->A
        session_fwd = EconomicSyncSession(
            cluster_a_id="cluster-econ-001",
            cluster_b_id="cluster-econ-002",
        )
        state_a = _create_economic_state("cluster-econ-001")
        state_b = _create_economic_state("cluster-econ-002")
        session_fwd.exchange_state("cluster-econ-001", state_a)
        session_fwd.exchange_state("cluster-econ-002", state_b)
        fwd_comparison = session_fwd.compare_hashes()

        # Reverse: B->A then A->B
        session_rev = EconomicSyncSession(
            cluster_a_id="cluster-econ-001",
            cluster_b_id="cluster-econ-002",
        )
        session_rev.exchange_state("cluster-econ-002", state_b)
        session_rev.exchange_state("cluster-econ-001", state_a)
        rev_comparison = session_rev.compare_hashes()

        assert fwd_comparison["match"] == rev_comparison["match"]
