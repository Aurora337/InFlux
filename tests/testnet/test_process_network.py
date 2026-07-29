"""
Tests for process-based testnet networking.

Tests that real node processes can form a network
and communicate over real sockets.
"""

import pytest
from influx.testnet.network_bootstrap import NetworkBootstrapper


class TestProcessNetwork:
    """Test suite for process-based network formation."""

    @pytest.fixture
    def bootstrapper(self):
        """Create a NetworkBootstrapper instance."""
        b = NetworkBootstrapper(base_port=9500)
        yield b
        b.shutdown()

    def test_bootstrap_single_node(self, bootstrapper):
        """Test bootstrapping a single node."""
        topology = bootstrapper.bootstrap(node_count=1)
        assert topology is not None
        assert topology.node_count == 1
        assert topology.all_running

    def test_bootstrap_four_nodes(self, bootstrapper):
        """Test bootstrapping four nodes."""
        topology = bootstrapper.bootstrap(node_count=4)
        assert topology is not None
        assert topology.node_count == 4
        assert topology.all_running

    def test_ring_topology(self, bootstrapper):
        """Test ring topology formation."""
        topology = bootstrapper.bootstrap(node_count=3)
        assert topology.node_count == 3
        assert topology.all_running

    def test_full_mesh_topology(self, bootstrapper):
        """Test full mesh topology formation."""
        topology = bootstrapper.bootstrap(node_count=4)
        bootstrapper.form_full_mesh()
        assert topology.all_running

    def test_star_topology(self, bootstrapper):
        """Test star topology formation."""
        topology = bootstrapper.bootstrap(node_count=5)
        bootstrapper.form_star_topology(center_index=0)
        assert topology.all_running

    def test_node_ports_unique(self, bootstrapper):
        """Test that each node gets a unique port."""
        topology = bootstrapper.bootstrap(node_count=4)
        ports = [n.port for n in topology.nodes]
        assert len(ports) == len(set(ports)), "Ports must be unique"

    def test_node_ids_unique(self, bootstrapper):
        """Test that each node has a unique ID."""
        topology = bootstrapper.bootstrap(node_count=4)
        node_ids = [n.node_id for n in topology.nodes]
        assert len(node_ids) == len(set(node_ids)), "Node IDs must be unique"

    def test_shutdown_cleans_up(self, bootstrapper):
        """Test that shutdown cleans up all processes."""
        bootstrapper.bootstrap(node_count=3)
        results = bootstrapper.shutdown()
        assert len(results) == 3
        assert all(results.values()), "All nodes should stop successfully"

    def test_snapshot_contains_metadata(self, bootstrapper):
        """Test that snapshot contains expected metadata."""
        bootstrapper.bootstrap(node_count=2)
        snapshot = bootstrapper.snapshot()
        assert "process_manager" in snapshot
        assert "topology" in snapshot
