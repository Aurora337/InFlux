"""
Test deterministic convergence with 10 nodes.
Minimum viable network size.
"""

import pytest
from harness.deterministic import DeterministicValidator
from harness.deterministic.assertions import ConvergenceAssertions


class TestDeterministic10Nodes:
    """Test suite for 10-node deterministic convergence."""

    def test_10_nodes_converge(self):
        """All 10 honest nodes should converge to identical state."""
        validator = DeterministicValidator(node_count=10, rounds=25)
        result = validator.validate()

        assert result.all_nodes_converged, (
            f"10 nodes failed to converge: {result.failure_reason}"
        )
        assert result.divergence_count == 0, (
            f"Divergence detected in {result.divergence_count} nodes"
        )
        assert result.ledger_hashes_match, "Ledger hashes do not match"
        assert result.state_roots_match, "State roots do not match"
        assert result.economic_states_match, "Economic states do not match"

    def test_10_nodes_assertions(self):
        """Convergence assertions should pass for 10 nodes."""
        validator = DeterministicValidator(node_count=10, rounds=25)
        validator.initialize_nodes()
        nodes = validator.nodes

        # Run a few rounds
        for _ in range(5):
            validator.run_consensus_round()

        # Assertions should pass
        assert ConvergenceAssertions.assert_ledger_hashes_match(nodes)
        assert ConvergenceAssertions.assert_state_roots_match(nodes)
        assert ConvergenceAssertions.assert_economic_states_match(nodes)
        assert ConvergenceAssertions.assert_full_convergence(nodes)
        assert ConvergenceAssertions.assert_honest_majority(nodes)

    def test_10_nodes_validation_result(self):
        """ValidationResult should contain correct metadata."""
        validator = DeterministicValidator(node_count=10, rounds=25)
        result = validator.validate()

        assert result.node_count == 10
        assert result.rounds_executed > 0
        assert ConvergenceAssertions.assert_validation_passed(result)
        assert ConvergenceAssertions.assert_no_divergence(result)
        assert ConvergenceAssertions.assert_rounds_completed(result, minimum_rounds=1)

    def test_10_nodes_summary(self):
        """Validator summary should reflect correct statistics."""
        validator = DeterministicValidator(node_count=10, rounds=25)
        validator.validate()
        summary = validator.summary()

        assert summary["status"] != "no_runs"
        assert summary["total_runs"] > 0
        assert summary["total_nodes_tested"] >= 10
