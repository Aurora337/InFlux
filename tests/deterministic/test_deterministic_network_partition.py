"""
Test deterministic convergence under network partition scenarios.
Tests that nodes reconverge after partition heals.
"""

import pytest
from harness.deterministic import DeterministicValidator
from harness.deterministic.assertions import ConvergenceAssertions
from harness.deterministic.scenarios import FaultScenarios


class TestDeterministicNetworkPartition:
    """Test suite for network partition scenarios."""

    def test_network_partition_convergence(self):
        """Nodes should reconverge after network partition."""
        result = FaultScenarios.run_network_partition()
        assert result.all_nodes_converged, (
            f"Network partition scenario failed: {result.failure_reason}"
        )
        assert ConvergenceAssertions.assert_validation_passed(result)

    def test_network_partition_no_divergence(self):
        """No divergence should occur after partition heals."""
        result = FaultScenarios.run_network_partition()
        assert ConvergenceAssertions.assert_no_divergence(result)

    def test_network_partition_metadata(self):
        """Partition scenario result should contain correct metadata."""
        result = FaultScenarios.run_network_partition()
        assert result.node_count == 20
        assert result.rounds_executed > 0

    def test_partition_validator_initialization(self):
        """Validator with network partition should initialize correctly."""
        validator = DeterministicValidator(
            node_count=20,
            rounds=75,
            network_partition=True,
        )
        validator.initialize_nodes()
        assert len(validator.nodes) == 20
        assert all(n.is_honest for n in validator.nodes)

    def test_partition_does_not_break_honest_majority(self):
        """Network partition should not break honest majority."""
        validator = DeterministicValidator(
            node_count=20,
            rounds=75,
            network_partition=True,
        )
        validator.initialize_nodes()
        nodes = validator.nodes
        assert ConvergenceAssertions.assert_honest_majority(nodes)

    def test_partition_scenario_in_summary(self):
        """Network partition should appear in fault scenarios summary."""
        summary = FaultScenarios.summary()
        assert "network_partition" in summary["details"]
        details = summary["details"]["network_partition"]
        assert details["nodes"] == 20
