"""
Convergence assertions for deterministic validation.

Asserts that every honest node ends with identical:
- Ledger hash
- State root
- Economic state
"""

from __future__ import annotations

from typing import Any

from ..deterministic_validator import NodeState, ValidationResult


class ConvergenceAssertions:
    """
    Assertions that verify deterministic convergence across nodes.

    These assertions are the core proof that the InFlux protocol
    behaves deterministically under all tested conditions.
    """

    @staticmethod
    def assert_ledger_hashes_match(nodes: list[NodeState]) -> bool:
        """
        Assert that all honest nodes have identical ledger hashes.

        Returns True if all match, raises AssertionError otherwise.
        """
        honest_nodes = [n for n in nodes if n.is_honest]
        if not honest_nodes:
            raise AssertionError("No honest nodes to compare")

        first_hash = honest_nodes[0].ledger_hash
        for node in honest_nodes[1:]:
            if node.ledger_hash != first_hash:
                raise AssertionError(
                    f"Ledger hash mismatch: {node.node_id} has "
                    f"'{node.ledger_hash}', expected '{first_hash}'"
                )
        return True

    @staticmethod
    def assert_state_roots_match(nodes: list[NodeState]) -> bool:
        """
        Assert that all honest nodes have identical state roots.

        Returns True if all match, raises AssertionError otherwise.
        """
        honest_nodes = [n for n in nodes if n.is_honest]
        if not honest_nodes:
            raise AssertionError("No honest nodes to compare")

        first_root = honest_nodes[0].state_root
        for node in honest_nodes[1:]:
            if node.state_root != first_root:
                raise AssertionError(
                    f"State root mismatch: {node.node_id} has "
                    f"'{node.state_root}', expected '{first_root}'"
                )
        return True

    @staticmethod
    def assert_economic_states_match(nodes: list[NodeState]) -> bool:
        """
        Assert that all honest nodes have identical economic states.

        Returns True if all match, raises AssertionError otherwise.
        """
        honest_nodes = [n for n in nodes if n.is_honest]
        if not honest_nodes:
            raise AssertionError("No honest nodes to compare")

        first_state = honest_nodes[0].economic_state
        for node in honest_nodes[1:]:
            if node.economic_state != first_state:
                raise AssertionError(
                    f"Economic state mismatch: {node.node_id} has "
                    f"state {node.economic_state}, expected {first_state}"
                )
        return True

    @staticmethod
    def assert_full_convergence(nodes: list[NodeState]) -> bool:
        """
        Assert complete convergence: ledger hashes, state roots,
        and economic states all match across all honest nodes.

        Returns True if all converge, raises AssertionError otherwise.
        """
        ConvergenceAssertions.assert_ledger_hashes_match(nodes)
        ConvergenceAssertions.assert_state_roots_match(nodes)
        ConvergenceAssertions.assert_economic_states_match(nodes)
        return True

    @staticmethod
    def assert_validation_passed(result: ValidationResult) -> bool:
        """
        Assert that a ValidationResult indicates successful convergence.

        Returns True if passed, raises AssertionError otherwise.
        """
        if not result.all_nodes_converged:
            raise AssertionError(
                f"Validation failed: {result.failure_reason}. "
                f"Node count: {result.node_count}, "
                f"Rounds: {result.rounds_executed}, "
                f"Divergences: {result.divergence_count}"
            )
        return True

    @staticmethod
    def assert_no_divergence(result: ValidationResult) -> bool:
        """
        Assert zero divergence across all nodes.

        Returns True if no divergence, raises AssertionError otherwise.
        """
        if result.divergence_count > 0:
            raise AssertionError(
                f"Divergence detected: {result.divergence_count} "
                f"nodes diverged from consensus"
            )
        return True

    @staticmethod
    def assert_rounds_completed(
        result: ValidationResult,
        minimum_rounds: int = 1,
    ) -> bool:
        """
        Assert that a minimum number of consensus rounds completed.

        Returns True if met, raises AssertionError otherwise.
        """
        if result.rounds_executed < minimum_rounds:
            raise AssertionError(
                f"Insufficient rounds: {result.rounds_executed} "
                f"completed, minimum {minimum_rounds} required"
            )
        return True

    @staticmethod
    def assert_honest_majority(nodes: list[NodeState]) -> bool:
        """
        Assert that honest nodes constitute a majority (> 2/3).

        Returns True if met, raises AssertionError otherwise.
        """
        total = len(nodes)
        honest = sum(1 for n in nodes if n.is_honest)
        if honest <= 2 * total / 3:
            raise AssertionError(
                f"Honest majority not maintained: {honest}/{total} "
                f"nodes are honest (need > 2/3)"
            )
        return True
