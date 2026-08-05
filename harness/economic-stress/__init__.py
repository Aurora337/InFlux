"""
Economic stress test suite for InFlux protocol.

Tests economic resilience under adversarial conditions:
- Whale accumulation
- Panic selling
- Dead network
- Explosive adoption
- Slow adoption
- Spam attacks
- Validator dropout
- Exchange outage
"""

from .economic_stress_engine import EconomicStressEngine, StressResult
from .metrics.economic_metrics import EconomicMetrics

__all__ = [
    "EconomicStressEngine",
    "StressResult",
    "EconomicMetrics",
]
