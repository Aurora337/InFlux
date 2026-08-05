from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExecutionContext:
    """
    Immutable execution context.
    """

    block_height: int
    transaction_id: str
    caller: str
    network_id: str