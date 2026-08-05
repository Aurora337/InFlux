"""
Fault scenarios for deterministic validation.

Tests convergence under various fault conditions:
- Leader failures
- Network partitions
- Node reconnection after failure
"""

from __future__ import annotations

from ..deterministic_validator import DeterministicValidator, ValidationResult


class FaultScenarios:
    """
    Fault tolerance convergence scenarios.

    Each scenario validates that honest nodes converge to
    identical state despite various fault conditions.
    """

    @staticmethod
    def run_leader_failure() -> ValidationResult:
        """
        Run validation with leader failures injected.
        Tests that consensus recovers after leader loss.
        """
        validator = DeterministicValidator(
            node_count=10,
            rounds=50,
            fault_injection=True,
        )
        return validator.validate()

    @staticmethod
    def run_network_partition() -> ValidationResult:
        """
        Run validation with network partitions.
        Tests that nodes reconverge after partition heals.
        """
        validator = DeterministicValidator(
            node_count=20,
            rounds=75,
            network_partition=True,
        )
        return validator.validate()

    @staticmethod
    def run_reconnection() -> ValidationResult:
        """
        Run validation simulating node reconnection.
        Tests that reconnecting nodes catch up to consensus.
        """
        validator = DeterministicValidator(
            node_count=15,
            rounds=60,
            fault_injection=True,
        )
        return validator.validate()

    @staticmethod
    def run_all() -> dict[str, ValidationResult]:
        """
        Run all fault scenarios.

        Returns a dictionary mapping scenario names to results.
        """
        return {
            "leader_failure": FaultScenarios.run_leader_failure(),
            "network_partition": FaultScenarios.run_network_partition(),
            "reconnection": FaultScenarios.run_reconnection(),
        }

    @staticmethod
    def summary() -> dict[str, object]:
        """
        Run all scenarios and return a summary.
        """
        results = FaultScenarios.run_all()
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
