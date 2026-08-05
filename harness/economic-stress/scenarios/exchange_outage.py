"""
Exchange outage scenario.

Simulates a major exchange going offline, testing liquidity and price stability.
"""

from ..economic_stress_engine import EconomicState


class ExchangeOutageScenario:
    """Simulates exchange outage affecting liquidity."""

    @staticmethod
    def run(state: EconomicState) -> None:
        """Apply exchange outage conditions for one round."""
        # Liquidity drops sharply
        state.reserve *= 0.95  # Reserve drops 5% per round
        # Price becomes volatile
        import random
        state.price *= (0.95 + random.random() * 0.10)  # 5% down to 5% up
        # Transaction volume drops
        state.transactions = int(state.transactions * 0.7)
        # Supply stable but slightly reduced
        state.supply *= 0.999
