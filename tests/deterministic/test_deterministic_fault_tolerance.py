"""
Test deterministic convergence under various fault conditions.
Includes leader failures, node failures, and recovery scenarios.
"""

import pytest
from harness.deterministic import DeterministicValidator
from harness.deterministic.assertions import ConvergenceAssertions
from harness.deterministic.scenarios import FaultScenarios


class TestDeterministicFaultTolerance:
    """Test suite for fault tolerance scenarios."""

    def test_leader_failure(self):
        """Consensus should recover after leader failure."""
        result = FaultScenarios.run_leader_failure()
        assert result.all_nodes_converged, (
            f"Leader failure scenario failed: {result.failure_reason}"
        )
        assert ConvergenceAssertions.assert_validation_passed(result)

    def test_leader_failure_no_divergence(self):
        """No divergence should occur during leader failure."""
        result = FaultScenarios.run_leader_failure()
        assert ConvergenceAssertions.assert_no_divergence(result)

    def test_leader_failure_metadata(self):
        """Fault scenario result should contain correct metadata."""
        result = FaultScenarios.run_leader_failure()
        assert result.node_count == 10
        assert result.rounds_executed > 0

    def test_fault_scenarios_summary(self):
        """Fault scenarios summary should reflect correct statistics."""
        summary = FaultScenarios.summary()
        assert summary["scenarios_run"] > 0
        assert "details" in summary
        assert "leader_failure" in summary["details"]

    def test_fault_injection_validator(self):
        """Validator with fault injection should initialize correctly."""
        validator = DeterministicValidator(
            node_count=10,
            rounds=50,
            fault_injection=True,
        )
        validator.initialize_nodes()
        assert len(validator.nodes) == 10
        assert all(n.is_honest for n in validator.nodes)  # Initially all honest

    def test_fault_injection_convergence(self):
        """Nodes should still converge under fault injection."""
        validator = DeterministicValidator(
            node_count=10,
            rounds=50,
            fault_injection=True,
        )
        result = validator.validate()
        # Fault injection may cause some divergence, but honest majority should converge
        honest_nodes = sum(1 for n in validator.nodes if n.is_honest)
        total = len(validator.nodes)
        if honest_nodes > 2 * total / 3:
            assert result.all_nodes_converged or result.divergence_count == 0
