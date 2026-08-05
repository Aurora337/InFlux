"""
Slow adoption scenario.

Simulates gradual network growth over an extended period.
"""

from ..economic_stress_engine import EconomicState


class SlowAdoptionScenario:
    """Simulates slow, steady adoption growth."""

    @staticmethod
    def run(state: EconomicState) -> None:
        """Apply slow adoption conditions for one round."""
        # Gradual participant growth
        state.participants = int(state.participants * 1.005)  # 0.5% growth per round
        # Steady supply growth
        state.supply *= 1.001  # 0.1% supply expansion
        state.reserve *= 1.0008  # 0.08% reserve growth
        state.price *= 1.0001  # Minimal price change
        state.transactions += int(state.participants * 0.05)  # Low transaction volume
