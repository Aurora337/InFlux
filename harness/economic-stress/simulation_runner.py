"""Run economic simulations over different time horizons."""

import sys
sys.path.insert(0, "src")

from influx.kernel.state import State
from influx.kernel.economic.delta_c import compute_delta


class EconomicSimulator:
    def __init__(self, initial_state: State):
        self.initial_state = initial_state
        self.current_state = initial_state
        self.history = [initial_state]

    def step(self) -> State:
        """Execute one epoch transition."""
        delta = compute_delta(self.current_state.supply, self.current_state.participants)
        
        self.current_state = State(
            epoch=self.current_state.epoch + 1,
            supply=self.current_state.supply + delta,
            participants=self.current_state.participants,
        )
        
        self.history.append(self.current_state)
        return self.current_state

    def run_epochs(self, num_epochs: int) -> list[State]:
        """Run simulation for N epochs."""
        for _ in range(num_epochs):
            self.step()
        return self.history

    def simulate_timeframe(self, timeframe_days: int, epochs_per_day: int = 1) -> list[State]:
        """
        Simulate for a given number of days.
        Default: 1 epoch per day (can be adjusted for finer granularity).
        """
        num_epochs = timeframe_days * epochs_per_day
        return self.run_epochs(num_epochs)


__all__ = ["EconomicSimulator"]
