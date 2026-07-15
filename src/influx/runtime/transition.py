from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .context import ExecutionContext
from .errors import StateTransitionError
from .state import RuntimeState


@dataclass(slots=True)
class ExecutionReceipt:
    """
    Result of a runtime state transition.
    """

    transaction_id: str
    success: bool
    changes: dict[str, Any] = field(default_factory=dict)


class StateTransitionEngine:
    """
    Deterministic runtime state transition processor.
    """

    def __init__(
        self,
        state: RuntimeState,
    ) -> None:
        self.state = state
        self.history: list[ExecutionReceipt] = []

    def apply(
        self,
        context: ExecutionContext,
        changes: dict[str, Any],
    ) -> ExecutionReceipt:
        """
        Apply deterministic state changes.
        """

        if not context.transaction_id:
            raise StateTransitionError(
                "missing transaction id"
            )

        for key, value in changes.items():
            self.state.set(
                key,
                value,
            )

        receipt = ExecutionReceipt(
            transaction_id=context.transaction_id,
            success=True,
            changes=changes,
        )

        self.history.append(receipt)

        return receipt

    def transition_count(
        self,
    ) -> int:
        """
        Return number of applied transitions.
        """

        return len(self.history)