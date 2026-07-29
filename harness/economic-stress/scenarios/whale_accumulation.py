"""
Whale accumulation scenario.

Simulates a single entity accumulating a large portion of the supply,
testing reserve stability and price impact.
"""

from ..economic_stress_engine import EconomicState


class WhaleAccumulationScenario:
    """Simulates whale accumulation pressure on the economy."""

    @staticmethod
    def run(state: EconomicState) -> None:
        """Apply whale accumulation pressure for one round."""
        # Whale accumulates 5% of supply per round
        whale_purchase = state.supply * 0.05
        state.reserve -= whale_purchase * 0.8
        state.supply *= 0.98  # Supply decreases as whale holds
        state.price *= 1.02  # Price increases due to demand
        state.transactions += 1  # One large transaction
