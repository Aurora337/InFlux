"""
Economic metrics for stress testing.

Measures:
- Reserve stability
- Reproduction rate
- Supply expansion
- Propagation speed
- Price stability
- Deterministic convergence
"""

from __future__ import annotations

from dataclasses import dataclass

from ..economic_stress_engine import EconomicState


@dataclass
class EconomicMetricsSnapshot:
    """Snapshot of economic metrics at a point in time."""

    reserve_ratio: float
    supply_growth_rate: float
    participant_growth_rate: float
    transaction_per_participant: float
    price_deviation: float
    reproduction_rate: float


class EconomicMetrics:
    """
    Computes and tracks economic metrics for stress testing.
    """

    def __init__(self):
        self._snapshots: list[EconomicMetricsSnapshot] = []

    def compute_snapshot(
        self,
        state: EconomicState,
        previous_state: EconomicState | None = None,
    ) -> EconomicMetricsSnapshot:
        """
        Compute a snapshot of economic metrics from current state.
        """
        reserve_ratio = state.reserve / state.supply if state.supply > 0 else 0.0

        supply_growth = 0.0
        participant_growth = 0.0
        reproduction = 0.0
        if previous_state:
            if previous_state.supply > 0:
                supply_growth = (state.supply - previous_state.supply) / previous_state.supply
            if previous_state.participants > 0:
                participant_growth = (state.participants - previous_state.participants) / previous_state.participants
            if previous_state.supply > 0:
                reproduction = (state.supply - previous_state.supply) / previous_state.supply

        tpp = state.transactions / max(state.participants, 1)
        price_dev = abs(1.0 - state.price)

        snapshot = EconomicMetricsSnapshot(
            reserve_ratio=reserve_ratio,
            supply_growth_rate=supply_growth,
            participant_growth_rate=participant_growth,
            transaction_per_participant=tpp,
            price_deviation=price_dev,
            reproduction_rate=reproduction,
        )
        self._snapshots.append(snapshot)
        return snapshot

    def compute_stability_score(self, snapshots: list[EconomicMetricsSnapshot] | None = None) -> float:
        """
        Compute overall economic stability score (0.0 to 1.0).
        """
        if snapshots is None:
            snapshots = self._snapshots
        if not snapshots:
            return 1.0

        avg_reserve = sum(s.reserve_ratio for s in snapshots) / len(snapshots)
        avg_growth = sum(s.supply_growth_rate for s in snapshots) / len(snapshots)
        avg_price = sum(s.price_deviation for s in snapshots) / len(snapshots)

        # Score based on reserve ratio target (0.5), positive growth, and price stability
        reserve_score = 1.0 - min(abs(avg_reserve - 0.5) * 2, 1.0)
        growth_score = 1.0 if avg_growth >= 0 else max(0, 1.0 + avg_growth * 10)
        price_score = 1.0 - min(avg_price * 10, 1.0)

        return (reserve_score * 0.4 + growth_score * 0.3 + price_score * 0.3)

    def get_snapshots(self) -> list[EconomicMetricsSnapshot]:
        """Return all recorded snapshots."""
        return list(self._snapshots)

    def summary(self) -> dict[str, float]:
        """Return a summary of all metrics."""
        if not self._snapshots:
            return {"stability_score": 1.0}

        return {
            "stability_score": self.compute_stability_score(),
            "avg_reserve_ratio": sum(s.reserve_ratio for s in self._snapshots) / len(self._snapshots),
            "avg_supply_growth": sum(s.supply_growth_rate for s in self._snapshots) / len(self._snapshots),
            "avg_participant_growth": sum(s.participant_growth_rate for s in self._snapshots) / len(self._snapshots),
            "avg_price_deviation": sum(s.price_deviation for s in self._snapshots) / len(self._snapshots),
        }
