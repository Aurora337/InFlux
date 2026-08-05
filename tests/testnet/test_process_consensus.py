"""
Tests for process-based consensus across real nodes.

Tests that consensus can be reached across multiple real node processes
communicating over real sockets.
"""

import pytest
from influx.testnet.testnet_orchestrator import TestnetOrchestrator


class TestProcessConsensus:
    """Test suite for process-based consensus."""

    @pytest.fixture
    def orchestrator(self):
        """Create a TestnetOrchestrator instance."""
        o = TestnetOrchestrator(base_port=9600)
        yield o

    def test_single_node_consensus(self, orchestrator):
        """Test consensus with a single node."""
        result = orchestrator.run_single_node_test()
        assert result.success, f"Single node test failed: {result.errors}"
        assert result.node_count == 1
        assert result.consensus_rounds >= 1

    def test_four_node_consensus(self, orchestrator):
        """Test consensus with four nodes."""
        result = orchestrator.run_four_node_test()
        assert result.success, f"Four node test failed: {result.errors}"
        assert result.node_count == 4
        assert result.consensus_rounds >= 3

    def test_ten_node_consensus(self, orchestrator):
        """Test consensus with ten nodes."""
        result = orchestrator.run_ten_node_test()
        assert result.success, f"Ten node test failed: {result.errors}"
        assert result.node_count == 10
        assert result.consensus_rounds >= 5

    def test_consensus_rounds_completed(self, orchestrator):
        """Test that all consensus rounds complete."""
        result = orchestrator.run_testnet(node_count=3, consensus_rounds=5, sync_rounds=0)
        assert result.success
        assert result.consensus_rounds == 5

    def test_sync_rounds_completed(self, orchestrator):
        """Test that all sync rounds complete."""
        result = orchestrator.run_testnet(node_count=3, consensus_rounds=0, sync_rounds=3)
        assert result.success
        assert result.sync_rounds == 3

    def test_total_rounds(self, orchestrator):
        """Test that total rounds equals consensus + sync."""
        result = orchestrator.run_testnet(node_count=3, consensus_rounds=4, sync_rounds=2)
        assert result.success
        assert result.rounds_completed == 6

    def test_result_contains_metadata(self, orchestrator):
        """Test that result contains expected metadata."""
        result = orchestrator.run_testnet(node_count=2, consensus_rounds=1, sync_rounds=1)
        assert result.success
        assert result.total_time > 0
        assert result.topology_snapshot is not None

    def test_no_errors_on_success(self, orchestrator):
        """Test that successful runs have no errors."""
        result = orchestrator.run_testnet(node_count=2, consensus_rounds=1, sync_rounds=1)
        assert result.success
        assert len(result.errors) == 0
