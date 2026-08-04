"""
Test deterministic convergence under recovery scenarios.
Tests that nodes recover and reconverge after failures.
"""

from harness.deterministic import DeterministicValidator
from harness.deterministic.assertions import ConvergenceAssertions
from harness.deterministic.scenarios import FaultScenarios, AdversarialScenarios


class TestDeterministicRecovery:
    """Test suite for recovery scenarios."""

    def test_reconnection_convergence(self):
        """Nodes should reconverge after reconnection."""
        result = FaultScenarios.run_reconnection()
        assert result.all_nodes_converged, (
            f"Reconnection scenario failed: {result.failure_reason}"
        )
        assert ConvergenceAssertions.assert_validation_passed(result)

    def test_reconnection_no_divergence(self):
        """No divergence should occur after reconnection."""
        result = FaultScenarios.run_reconnection()
        assert ConvergenceAssertions.assert_no_divergence(result)

    def test_reconnection_metadata(self):
        """Reconnection scenario result should contain correct metadata."""
        result = FaultScenarios.run_reconnection()
        assert result.node_count == 15
        assert result.rounds_executed > 0

    def test_recovery_after_adversarial(self):
        """Nodes should recover and converge after adversarial conditions."""
        result = AdversarialScenarios.run_all_adversarial()
        assert result.all_nodes_converged, (
            f"Adversarial recovery scenario failed: {result.failure_reason}"
        )
        assert ConvergenceAssertions.assert_validation_passed(result)

    def test_recovery_after_adversarial_no_divergence(self):
        """No divergence should occur after adversarial recovery."""
        result = AdversarialScenarios.run_all_adversarial()
        assert ConvergenceAssertions.assert_no_divergence(result)

    def test_recovery_after_adversarial_metadata(self):
        """Adversarial recovery result should contain correct metadata."""
        result = AdversarialScenarios.run_all_adversarial()
        assert result.node_count == 20
        assert result.rounds_executed > 0

    def test_recovery_scenario_in_summary(self):
        """Reconnection should appear in fault scenarios summary."""
        summary = FaultScenarios.summary()
        assert "reconnection" in summary["details"]
        details = summary["details"]["reconnection"]
        assert details["nodes"] == 15

    def test_adversarial_scenario_in_summary(self):
        """All adversarial should appear in adversarial scenarios summary."""
        summary = AdversarialScenarios.summary()
        assert "all_adversarial" in summary["details"]
        details = summary["details"]["all_adversarial"]
        assert details["nodes"] == 20

    def test_recovery_validator_initialization(self):
        """Validator with recovery should initialize correctly."""
        validator = DeterministicValidator(
            node_count=15,
            rounds=60,
            fault_injection=True,
        )
        validator.initialize_nodes()
        assert len(validator.nodes) == 15
        assert all(n.is_honest for n in validator.nodes)

    def test_recovery_maintains_honest_majority(self):
        """Recovery should maintain honest majority."""
        validator = DeterministicValidator(
            node_count=15,
            rounds=60,
            fault_injection=True,
        )
        validator.initialize_nodes()
        nodes = validator.nodes
        assert ConvergenceAssertions.assert_honest_majority(nodes)
