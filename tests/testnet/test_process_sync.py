"""
Tests for process-based synchronization across real nodes.

Tests that state synchronization works correctly across multiple
real node processes communicating over real sockets.
"""

import pytest
from influx.testnet.testnet_orchestrator import TestnetOrchestrator
from influx.testnet.network_bootstrap import NetworkBootstrapper


class TestProcessSync:
    """Test suite for process-based synchronization."""

    @pytest.fixture
    def bootstrapper(self):
        """Create a NetworkBootstrapper instance."""
        b = NetworkBootstrapper(base_port=9700)
        yield b
        b.shutdown()

    @pytest.fixture
    def orchestrator(self):
        """Create a TestnetOrchestrator instance."""
        o = TestnetOrchestrator(base_port=9800)
        yield o

    def test_single_node_sync(self, orchestrator):
        """Test sync with a single node."""
        result = orchestrator.run_testnet(node_count=1, consensus_rounds=0, sync_rounds=2)
        assert result.success, f"Single node sync failed: {result.errors}"
        assert result.sync_rounds >= 2

    def test_four_node_sync(self, orchestrator):
        """Test sync with four nodes."""
        result = orchestrator.run_testnet(node_count=4, consensus_rounds=0, sync_rounds=3)
        assert result.success, f"Four node sync failed: {result.errors}"
        assert result.sync_rounds == 3

    def test_bootstrap_network_topology(self, bootstrapper):
        """Test topology formation during bootstrap."""
        topology = bootstrapper.bootstrap(node_count=3)
        assert topology is not None
        assert topology.node_count == 3
        assert topology.all_running
        snapshot = topology.snapshot()
        assert snapshot["node_count"] == 3
        assert snapshot["all_running"] is True

    def test_bootstrap_ring_formation(self, bootstrapper):
        """Test ring topology formation."""
        bootstrapper.bootstrap(node_count=4)
        bootstrapper.form_full_mesh()
        snapshot = bootstrapper.snapshot()
        assert snapshot["topology"] is not None

    def test_network_stability(self, bootstrapper):
        """Test network stability after bootstrap."""
        bootstrapper.bootstrap(node_count=3)
        stable = bootstrapper.wait_for_stability(timeout=5.0)
        assert stable, "Network should reach stable state"

    def test_shutdown_cleanup(self, bootstrapper):
        """Test that shutdown properly cleans up all resources."""
        bootstrapper.bootstrap(node_count=3)
        results = bootstrapper.shutdown()
        assert len(results) == 3
        assert all(results.values())
