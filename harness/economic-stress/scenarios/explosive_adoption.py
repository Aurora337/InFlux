"""
Explosive adoption scenario.

Simulates rapid network growth, testing scalability of economic parameters.
"""

from ..economic_stress_engine import EconomicState


class ExplosiveAdoptionScenario:
    """Simulates explosive adoption with rapid participant growth."""

    @staticmethod
    def run(state: EconomicState) -> None:
        """Apply explosive adoption pressure for one round."""
        # Rapid participant growth
        state.participants = int(state.participants * 1.10)  # 10% growth per round
        # Supply grows to accommodate new participants
        state.supply *= 1.02  # 2% supply expansion
        state.reserve *= 1.015  # 1.5% reserve growth
        state.price *= 1.005  # Slight price increase from demand
        state.transactions += int(state.participants * 0.3)  # Transaction volume grows
