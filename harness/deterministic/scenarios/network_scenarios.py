"""
Network scenarios for deterministic validation.

Tests convergence under various network sizes:
- 10 nodes (minimum viable network)
- 100 nodes (moderate network)
- 1000 nodes (large network)
"""

from __future__ import annotations

from ..deterministic_validator import DeterministicValidator, ValidationResult


class NetworkScenarios:
    """
    Network size convergence scenarios.

    Each scenario validates that all honest nodes converge
    to identical state under specified network conditions.
    """

    @staticmethod
    def run_10_nodes() -> ValidationResult:
        """
        Run deterministic validation with 10 nodes.
        Minimum viable network size.
        """
        validator = DeterministicValidator(
            node_count=10,
            rounds=25,
        )
        return validator.validate()

    @staticmethod
    def run_100_nodes() -> ValidationResult:
        """
        Run deterministic validation with 100 nodes.
        Moderate network size with higher coordination overhead.
        """
        validator = DeterministicValidator(
            node_count=100,
            rounds=50,
        )
        return validator.validate()

    @staticmethod
    def run_1000_nodes() -> ValidationResult:
        """
        Run deterministic validation with 1000 nodes.
        Large network size testing scalability of consensus.
        """
        validator = DeterministicValidator(
            node_count=1000,
            rounds=100,
        )
        return validator.validate()

    @staticmethod
    def run_all() -> dict[str, ValidationResult]:
        """
        Run all network size scenarios.

        Returns a dictionary mapping scenario names to results.
        """
        return {
            "10_nodes": NetworkScenarios.run_10_nodes(),
            "100_nodes": NetworkScenarios.run_100_nodes(),
            "1000_nodes": NetworkScenarios.run_1000_nodes(),
        }

    @staticmethod
    def summary() -> dict[str, object]:
        """
        Run all scenarios and return a summary.
        """
        results = NetworkScenarios.run_all()
        total = len(results)
        passed = sum(1 for r in results.values() if r.all_nodes_converged)
        return {
            "scenarios_run": total,
            "passed": passed,
            "failed": total - passed,
            "details": {
                name: {
                    "converged": r.all_nodes_converged,
                    "nodes": r.node_count,
                    "rounds": r.rounds_executed,
                    "divergences": r.divergence_count,
                }
                for name, r in results.items()
            },
        }
