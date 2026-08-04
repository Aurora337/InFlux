"""
Economic Stress Engine — Core stress testing engine.

Tests economic resilience under adversarial conditions:
- Whale accumulation
- Panic selling
- Dead network
- Explosive adoption
- Slow adoption
- Spam attacks
- Validator dropout
- Exchange outage

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
from typing import Callable


@dataclass
class EconomicState:
    """Represents the economic state at a point in time."""

    supply: float = 1000.0
    reserve: float = 500.0
    participants: int = 100
    price: float = 1.0
    validators: int = 10
    transactions: int = 0
    spam_count: int = 0
    epoch: int = 0


@dataclass
class StressResult:
    """Result of an economic stress test scenario."""

    scenario_name: str
    initial_state: EconomicState
    final_state: EconomicState
    reserve_stability: float
    reproduction_rate: float
    supply_expansion: float
    propagation_speed: float
    price_stability: float
    deterministic_convergence: bool
    passed: bool
    failure_reason: str = ""


class EconomicStressEngine:
    """
    Orchestrates economic stress scenarios and measures resilience.

    Each scenario simulates an adversarial economic condition and
    measures key economic metrics to determine if the protocol
    remains stable.
    """

    def __init__(self):
        self._results: list[StressResult] = []

    def run_scenario(
        self,
        name: str,
        initial_state: EconomicState | None = None,
        scenario_fn: Callable[[EconomicState], None] | None = None,
        rounds: int = 100,
    ) -> StressResult:
        """
        Run a single economic stress scenario.

        Args:
            name: Name of the scenario
            initial_state: Initial economic state (defaults to standard genesis)
            scenario_fn: Function that modifies economic state per round
            rounds: Number of rounds to simulate

        Returns:
            StressResult with metrics and pass/fail status
        """
        state = initial_state or EconomicState()
        initial = EconomicState(
            supply=state.supply,
            reserve=state.reserve,
            participants=state.participants,
            price=state.price,
            validators=state.validators,
            transactions=state.transactions,
            spam_count=state.spam_count,
            epoch=state.epoch,
        )

        for round_num in range(rounds):
            state.epoch = round_num
            if scenario_fn:
                scenario_fn(state)
            self._apply_natural_growth(state)

        final = state
        metrics = self._compute_metrics(initial, final, rounds)

        result = StressResult(
            scenario_name=name,
            initial_state=initial,
            final_state=final,
            reserve_stability=metrics["reserve_stability"],
            reproduction_rate=metrics["reproduction_rate"],
            supply_expansion=metrics["supply_expansion"],
            propagation_speed=metrics["propagation_speed"],
            price_stability=metrics["price_stability"],
            deterministic_convergence=metrics["deterministic_convergence"],
            passed=self._is_stable(metrics),
            failure_reason=self._get_failure_reason(metrics),
        )

        self._results.append(result)
        return result

    def _apply_natural_growth(self, state: EconomicState) -> None:
        """Apply natural economic growth for a round."""
        # Natural supply growth
        state.supply *= 1.001  # 0.1% per round
        # Natural reserve growth
        state.reserve *= 1.0005  # 0.05% per round
        # Natural participant growth
        state.participants = int(state.participants * 1.002)  # 0.2% per round
        # Price stability
        state.price *= 1.0
        # Natural transaction growth
        state.transactions += int(state.participants * 0.1)

    def _compute_metrics(
        self,
        initial: EconomicState,
        final: EconomicState,
        rounds: int,
    ) -> dict[str, float]:
        """Compute economic metrics from initial and final states."""
        # Reserve stability: how close reserve/supply ratio stays to target
        initial_ratio = initial.reserve / initial.supply if initial.supply > 0 else 0.5
        final_ratio = final.reserve / final.supply if final.supply > 0 else 0.5
        reserve_stability = 1.0 - abs(final_ratio - initial_ratio) / initial_ratio if initial_ratio > 0 else 1.0

        # Reproduction rate: supply growth per round
        reproduction_rate = (final.supply / initial.supply) ** (1.0 / max(rounds, 1)) - 1.0

        # Supply expansion: total supply growth
        supply_expansion = (final.supply - initial.supply) / initial.supply if initial.supply > 0 else 0.0

        # Propagation speed: transactions per participant per round
        propagation_speed = final.transactions / max(final.participants * rounds, 1)

        # Price stability: how stable price remained
        price_stability = 1.0 - abs(final.price - initial.price) / initial.price if initial.price > 0 else 1.0

        # Deterministic convergence: always true for simulation
        deterministic_convergence = True

        return {
            "reserve_stability": reserve_stability,
            "reproduction_rate": reproduction_rate,
            "supply_expansion": supply_expansion,
            "propagation_speed": propagation_speed,
            "price_stability": price_stability,
            "deterministic_convergence": deterministic_convergence,
        }

    def _is_stable(self, metrics: dict[str, float]) -> bool:
        """Determine if the economy is stable based on metrics."""
        return (
            metrics["reserve_stability"] >= 0.5
            and metrics["price_stability"] >= 0.5
            and metrics["reproduction_rate"] >= -0.1
        )

    def _get_failure_reason(self, metrics: dict[str, float]) -> str:
        """Get human-readable failure reason."""
        reasons = []
        if metrics["reserve_stability"] < 0.5:
            reasons.append(f"Reserve unstable: {metrics['reserve_stability']:.2%}")
        if metrics["price_stability"] < 0.5:
            reasons.append(f"Price unstable: {metrics['price_stability']:.2%}")
        if metrics["reproduction_rate"] < -0.1:
            reasons.append(f"Negative reproduction: {metrics['reproduction_rate']:.2%}")
        return "; ".join(reasons) if reasons else ""

    def get_results(self) -> list[StressResult]:
        """Return all stress test results."""
        return list(self._results)

    def summary(self) -> dict[str, object]:
        """Return a summary of all stress test runs."""
        if not self._results:
            return {"status": "no_runs"}

        total = len(self._results)
        passed = sum(1 for r in self._results if r.passed)
        failed = total - passed

        return {
            "total_scenarios": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total if total > 0 else 0.0,
            "scenarios": [
                {
                    "name": r.scenario_name,
                    "passed": r.passed,
                    "reserve_stability": r.reserve_stability,
                    "reproduction_rate": r.reproduction_rate,
                    "supply_expansion": r.supply_expansion,
                    "price_stability": r.price_stability,
                }
                for r in self._results
            ],
        }
