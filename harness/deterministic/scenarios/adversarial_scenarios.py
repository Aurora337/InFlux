"""
Adversarial scenarios for deterministic validation.

Tests convergence under adversarial network conditions:
- Packet reordering
- Message duplication
- Random latency
"""

from __future__ import annotations

from ..deterministic_validator import DeterministicValidator, ValidationResult


class AdversarialScenarios:
    """
    Adversarial network condition scenarios.

    Each scenario validates that honest nodes converge to
    identical state despite adversarial network conditions.
    """

    @staticmethod
    def run_packet_reordering() -> ValidationResult:
        """
        Run validation with packet reordering.
        Tests that consensus is resilient to out-of-order delivery.
        """
        validator = DeterministicValidator(
            node_count=10,
            rounds=50,
            packet_reordering=True,
        )
        return validator.validate()

    @staticmethod
    def run_message_duplication() -> ValidationResult:
        """
        Run validation with message duplication.
        Tests that consensus handles duplicate messages correctly.
        """
        validator = DeterministicValidator(
            node_count=10,
            rounds=50,
            message_duplication=True,
        )
        return validator.validate()

    @staticmethod
    def run_random_latency() -> ValidationResult:
        """
        Run validation with random network latency.
        Tests that consensus converges despite variable delivery times.
        """
        validator = DeterministicValidator(
            node_count=10,
            rounds=75,
            random_latency=True,
        )
        return validator.validate()

    @staticmethod
    def run_all_adversarial() -> ValidationResult:
        """
        Run validation with ALL adversarial conditions simultaneously.
        Tests worst-case network conditions.
        """
        validator = DeterministicValidator(
            node_count=20,
            rounds=100,
            packet_reordering=True,
            message_duplication=True,
            random_latency=True,
        )
        return validator.validate()

    @staticmethod
    def run_all() -> dict[str, ValidationResult]:
        """
        Run all adversarial scenarios.

        Returns a dictionary mapping scenario names to results.
        """
        return {
            "packet_reordering": AdversarialScenarios.run_packet_reordering(),
            "message_duplication": AdversarialScenarios.run_message_duplication(),
            "random_latency": AdversarialScenarios.run_random_latency(),
            "all_adversarial": AdversarialScenarios.run_all_adversarial(),
        }

    @staticmethod
    def summary() -> dict[str, object]:
        """
        Run all scenarios and return a summary.
        """
        results = AdversarialScenarios.run_all()
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
