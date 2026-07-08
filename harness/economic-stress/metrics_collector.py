"""Collect and track economic metrics from simulations."""

from dataclasses import dataclass


@dataclass
class EconomicMetrics:
    timeframe_name: str
    timeframe_days: int
    epochs_run: int
    initial_supply: float
    final_supply: float
    supply_growth_percent: float
    final_validators: int
    final_participation_percent: float
    reserve_balance: float  # placeholder for reserve tracking

    def to_dict(self) -> dict:
        return {
            "timeframe": self.timeframe_name,
            "days": self.timeframe_days,
            "epochs": self.epochs_run,
            "supply": {
                "initial": self.initial_supply,
                "final": self.final_supply,
                "growth_percent": self.supply_growth_percent,
            },
            "validators": self.final_validators,
            "participation_percent": self.final_participation_percent,
            "reserve_balance": self.reserve_balance,
        }


class MetricsCollector:
    def __init__(self):
        self.results = []

    def collect_from_history(
        self,
        history: list,
        timeframe_name: str,
        timeframe_days: int,
    ) -> EconomicMetrics:
        """Analyze simulation history and extract metrics."""
        if not history:
            raise ValueError("History cannot be empty")

        initial_state = history[0]
        final_state = history[-1]

        initial_supply = initial_state.supply
        final_supply = final_state.supply
        supply_growth_percent = ((final_supply - initial_supply) / initial_supply) * 100

        metrics = EconomicMetrics(
            timeframe_name=timeframe_name,
            timeframe_days=timeframe_days,
            epochs_run=len(history) - 1,
            initial_supply=initial_supply,
            final_supply=final_supply,
            supply_growth_percent=supply_growth_percent,
            final_validators=final_state.participants,
            final_participation_percent=(final_state.participants / 100) * 100,
            reserve_balance=0.0,  # placeholder
        )

        self.results.append(metrics)
        return metrics

    def all_metrics(self) -> list[EconomicMetrics]:
        """Return all collected metrics."""
        return self.results


__all__ = ["EconomicMetrics", "MetricsCollector"]
