"""
InFlux v5.0.0 — Deterministic Economic Core.

Provides the deterministic execution infrastructure for all
economic operations in the InFlux protocol.

The Economic Core enforces the rule:
    No module modifies balances directly.
    All balance changes flow through EconomicExecutor.execute().

Architecture:
    EconomicEngine (orchestrator)
        ├── EconomicContext (execution context)
        ├── EconomicState (deterministic state)
        ├── EconomicTransition (state transitions)
        ├── EconomicSnapshot (state snapshots)
        ├── EconomicExecutor (single mutation path)
        ├── EconomicScheduler (event scheduling)
        ├── EconomicValidator (pre/post validation)
        └── EconomicMetrics (observation only)
"""

from influx.economics.economic_context import EconomicContext
from influx.economics.economic_state import (
    EconomicState,
    EconomicAccount,
    SupplyInfo,
    ReserveInfo,
)
from influx.economics.economic_transition import (
    EconomicTransition,
    StateTransition,
    TransitionType,
)
from influx.economics.economic_snapshot import (
    EconomicSnapshot,
    EconomicSnapshotManager,
)
from influx.economics.economic_executor import (
    EconomicExecutor,
    EconomicOperation,
    OperationType,
    ExecutionReceipt,
)
from influx.economics.economic_scheduler import EconomicScheduler
from influx.economics.economic_validator import EconomicValidator
from influx.economics.economic_metrics import EconomicMetrics
from influx.economics.economic_engine import EconomicEngine

__all__ = [
    "EconomicContext",
    "EconomicState",
    "EconomicAccount",
    "SupplyInfo",
    "ReserveInfo",
    "EconomicTransition",
    "StateTransition",
    "TransitionType",
    "EconomicSnapshot",
    "EconomicSnapshotManager",
    "EconomicExecutor",
    "EconomicOperation",
    "OperationType",
    "ExecutionReceipt",
    "EconomicScheduler",
    "EconomicValidator",
    "EconomicMetrics",
    "EconomicEngine",
]
