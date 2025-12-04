"""metrics_collector.py

Metrics collector placeholder: aggregate counters, histograms and simple statistics.
"""

from typing import Dict, List

class MetricsCollector:
    def __init__(self):
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}

    def inc(self, key: str, amount: int = 1) -> None:
        self.counters[key] = self.counters.get(key, 0) + amount

    def set_gauge(self, key: str, value: float) -> None:
        self.gauges[key] = value

    def snapshot(self) -> Dict[str, Dict]:
        return {"counters": dict(self.counters), "gauges": dict(self.gauges)}

__all__ = ["MetricsCollector"]