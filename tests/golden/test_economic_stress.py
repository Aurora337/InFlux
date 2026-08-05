"""Economic stress test harness."""

import sys
sys.path.insert(0, "src")
sys.path.insert(0, "harness/economic-stress")

from influx.kernel.state import State
from simulation_runner import EconomicSimulator
from metrics_collector import MetricsCollector
from stress_report import ReportGenerator


def test_economic_stress_1_day():
    """Run 1-day economic simulation."""
    initial_state = State(epoch=0, supply=1000.0, participants=100)
    simulator = EconomicSimulator(initial_state)
    history = simulator.simulate_timeframe(1, epochs_per_day=1)
    
    assert len(history) == 2  # initial + 1 epoch
    assert history[-1].epoch == 1
    assert history[-1].supply > initial_state.supply
    
    collector = MetricsCollector()
    metrics = collector.collect_from_history(history, "1 Day", 1)
    
    assert metrics.supply_growth_percent > 0
    assert metrics.final_validators == 100


def test_economic_stress_30_days():
    """Run 30-day economic simulation."""
    initial_state = State(epoch=0, supply=1000.0, participants=100)
    simulator = EconomicSimulator(initial_state)
    history = simulator.simulate_timeframe(30, epochs_per_day=1)
    
    assert len(history) == 31  # initial + 30 epochs
    assert history[-1].epoch == 30
    assert history[-1].supply > history[0].supply
    
    collector = MetricsCollector()
    metrics = collector.collect_from_history(history, "30 Days", 30)
    
    assert metrics.epochs_run == 30
    assert metrics.supply_growth_percent > 0


def test_economic_stress_365_days():
    """Run 365-day economic simulation."""
    initial_state = State(epoch=0, supply=1000.0, participants=100)
    simulator = EconomicSimulator(initial_state)
    history = simulator.simulate_timeframe(365, epochs_per_day=1)
    
    assert len(history) == 366  # initial + 365 epochs
    assert history[-1].epoch == 365
    
    collector = MetricsCollector()
    metrics = collector.collect_from_history(history, "1 Year", 365)
    
    assert metrics.epochs_run == 365
    # With base growth rate of 0.01 and 100 participants:
    # daily delta = supply * 0.01 * (100/100) = supply * 0.01
    # After 365 days, supply should grow significantly
    assert metrics.supply_growth_percent > 300


def test_economic_stress_10_years():
    """Run 10-year economic simulation."""
    initial_state = State(epoch=0, supply=1000.0, participants=100)
    simulator = EconomicSimulator(initial_state)
    history = simulator.simulate_timeframe(365 * 10, epochs_per_day=1)
    
    assert len(history) == 365 * 10 + 1
    assert history[-1].epoch == 365 * 10
    
    collector = MetricsCollector()
    metrics = collector.collect_from_history(history, "10 Years", 365 * 10)
    
    assert metrics.epochs_run == 3650
    # After 10 years of 1% daily growth per participant
    assert metrics.final_supply > initial_state.supply * 30


def test_economic_stress_full_harness():
    """Run full stress test across all timeframes and generate report."""
    timeframes = [
        (1, "1 Day"),
        (30, "30 Days"),
        (365, "1 Year"),
        (365 * 10, "10 Years"),
    ]
    
    collector = MetricsCollector()
    
    for days, name in timeframes:
        initial_state = State(epoch=0, supply=1000.0, participants=100)
        simulator = EconomicSimulator(initial_state)
        history = simulator.simulate_timeframe(days, epochs_per_day=1)
        collector.collect_from_history(history, name, days)
    
    generator = ReportGenerator()
    report = generator.generate(collector.all_metrics())
    
    # Verify we have all 4 timeframes
    assert len(collector.all_metrics()) == 4
    
    # Verify supply grows monotonically
    metrics_list = collector.all_metrics()
    for i in range(len(metrics_list) - 1):
        assert metrics_list[i].final_supply <= metrics_list[i + 1].final_supply
    
    # Generate and print report
    summary = report.summary()
    assert "ECONOMIC STRESS TEST REPORT" in summary
    assert "1 Day" in summary
    assert "10 Years" in summary
