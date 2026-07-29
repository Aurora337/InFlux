"""
Validator dropout scenario.

Simulates validators leaving the network, testing consensus and economic stability.
"""

from ..economic_stress_engine import EconomicState


class ValidatorDropoutScenario:
    """Simulates validators dropping out of the network."""

    @staticmethod
    def run(state: EconomicState) -> None:
        """Apply validator dropout conditions for one round."""
        # Validators leave each round
        dropout_count = max(1, state.validators // 5)  # 20% dropout per round
        state.validators = max(1, state.validators - dropout_count)
        # Network becomes less efficient
        state.reserve *= 0.99  # Reserve decreases from reduced validation
        state.supply *= 0.998  # Slight supply contraction
        state.price *= 0.99  # Price drops from reduced confidence
        state.transactions += int(state.participants * 0.02)  # Reduced activity
