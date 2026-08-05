"""
Panic selling scenario.

Simulates mass sell-off event, testing price stability and reserve resilience.
"""

from ..economic_stress_engine import EconomicState


class PanicSellingScenario:
    """Simulates panic selling pressure on the economy."""

    @staticmethod
    def run(state: EconomicState) -> None:
        """Apply panic selling pressure for one round."""
        # Mass sell-off: 10% of supply sold per round
        sell_volume = state.supply * 0.10
        state.reserve += sell_volume * 0.9
        state.supply *= 0.95  # Supply decreases as tokens are burned
        state.price *= 0.90  # Price drops 10% per round
        state.transactions += int(state.participants * 0.5)  # Many small sells
