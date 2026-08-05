"""
Dead network scenario.

Simulates a network with no new participants or transactions,
testing economic stability under stagnation.
"""

from ..economic_stress_engine import EconomicState


class DeadNetworkScenario:
    """Simulates a dead network with no activity."""

    @staticmethod
    def run(state: EconomicState) -> None:
        """Apply dead network conditions for one round."""
        # No new participants
        # No growth
        state.transactions = 0  # No transactions
        state.supply *= 1.0  # No supply growth
        state.reserve *= 0.999  # Slow reserve decay
        state.price *= 0.995  # Slow price decline
