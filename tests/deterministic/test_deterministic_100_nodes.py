"""
Test deterministic convergence with 100 nodes.
Moderate network size with higher coordination overhead.
"""

import pytest
from harness.deterministic import DeterministicValidator
from harness.deterministic.assertions import ConvergenceAssertions


class TestDeterministic100Nodes:
    """Test suite for 100-node deterministic convergence."""

    def test_100_nodes_converge(self):
        """All 100 honest nodes should converge to identical state."""
        validator = DeterministicValidator(node_count=100, rounds=50)
        result = validator.validate()

        assert result.all_nodes_converged, (
            f"100 nodes failed to converge: {result.failure_reason}"
        )
        assert result.divergence_count == 0, (
            f"Divergence detected in {result.divergence_count} nodes"
        )
        assert result.ledger_hashes_match, "Ledger hashes do not match"
        assert result.state_roots_match, "State roots do not match"
        assert result.economic_states_match, "Economic states do not match"

    def test_100_nodes_validation_result(self):
        """ValidationResult should contain correct metadata for 100 nodes."""
        validator = DeterministicValidator(node_count=100, rounds=50)
        result = validator.validate()

        assert result.node_count == 100
        assert result.rounds_executed > 0
        assert ConvergenceAssertions.assert_validation_passed(result)
        assert ConvergenceAssertions.assert_no_divergence(result)

    def test_100_nodes_summary(self):
        """Validator summary should reflect correct statistics."""
        validator = DeterministicValidator(node_count=100, rounds=50)
        validator.validate()
        summary = validator.summary()

        assert summary["status"] != "no_runs"
        assert summary["total_nodes_tested"] >= 100

    def test_100_nodes_honest_majority(self):
        """Honest majority should be maintained across rounds."""
        validator = DeterministicValidator(node_count=100, rounds=50)
        validator.initialize_nodes()
        nodes = validator.nodes

        assert ConvergenceAssertions.assert_honest_majority(nodes)
