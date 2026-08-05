"""
Deterministic validation suite for InFlux protocol.

Proves that every honest node ends with identical:
- Ledger hash
- State root
- Economic state
"""

from .deterministic_validator import DeterministicValidator
from .assertions.convergence_assertions import ConvergenceAssertions

__all__ = [
    "DeterministicValidator",
    "ConvergenceAssertions",
]
