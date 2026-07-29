"""
Spam attack scenario.

Simulates network spam with excessive transactions,
testing transaction processing and economic resilience.
"""

from ..economic_stress_engine import EconomicState


class SpamAttackScenario:
    """Simulates spam attack with excessive transaction volume."""

    @staticmethod
    def run(state: EconomicState) -> None:
        """Apply spam attack conditions for one round."""
        # Massive transaction volume
        spam_tx = int(state.participants * 10)  # 10x normal transaction volume
        state.transactions += spam_tx
        state.spam_count += spam_tx
        # Spam consumes network resources
        state.reserve *= 0.995  # Reserve decreases from spam costs
        state.supply *= 0.999  # Slight supply decrease from fees
        state.price *= 0.998  # Slight price pressure
