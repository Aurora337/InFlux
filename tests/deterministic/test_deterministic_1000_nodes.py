"""
Test deterministic convergence with 1000 nodes.
Large network size testing scalability of consensus.
"""

import pytest
from harness.deterministic import DeterministicValidator
from harness.deterministic.assertions import ConvergenceAssertions


class TestDeterministic1000Nodes:
    """Test suite for 1000-node deterministic convergence."""

    def test_1000_nodes_converge(self):
        """All 1000 honest nodes should converge to identical state."""
        validator = DeterministicValidator(node_count=1000, rounds=100)
        result = validator.validate()

        assert result.all_nodes_converged, (
            f"1000 nodes failed to converge: {result.failure_reason}"
        )
        assert result.divergence_count == 0, (
            f"Divergence detected in {result.divergence_count} nodes"
        )
        assert result.ledger_hashes_match, "Ledger hashes do not match"
        assert result.state_roots_match, "State roots do not match"
        assert result.economic_states_match, "Economic states do not match"

    def test_1000_nodes_validation_result(self):
        """ValidationResult should contain correct metadata for 1000 nodes."""
        validator = DeterministicValidator(node_count=1000, rounds=100)
        result = validator.validate()

        assert result.node_count == 1000
        assert result.rounds_executed > 0
        assert ConvergenceAssertions.assert_validation_passed(result)
        assert ConvergenceAssertions.assert_no_divergence(result)

    def test_1000_nodes_summary(self):
        """Validator summary should reflect correct statistics."""
        validator = DeterministicValidator(node_count=1000, rounds=100)
        validator.validate()
        summary = validator.summary()

        assert summary["status"] != "no_runs"
        assert summary["total_nodes_tested"] >= 1000

    def test_1000_nodes_honest_majority(self):
        """Honest majority should be maintained across rounds."""
        validator = DeterministicValidator(node_count=1000, rounds=100)
        validator.initialize_nodes()
        nodes = validator.nodes

        assert ConvergenceAssertions.assert_honest_majority(nodes)
