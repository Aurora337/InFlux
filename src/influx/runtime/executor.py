from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .context import ExecutionContext
from .errors import ExecutionError


class RuntimeExecutor:
    """
    Deterministic runtime execution engine.

    Executes runtime operations inside
    isolated execution contexts.
    """

    def __init__(self) -> None:
        self.executions: list[str] = []

    def execute(
        self,
        context: ExecutionContext,
        operation: Callable[[ExecutionContext], Any],
    ) -> Any:
        """
        Execute a runtime operation.
        """

        if not context.transaction_id:
            raise ExecutionError(
                "missing transaction id"
            )

        try:
            result = operation(context)

        except Exception as exc:
            raise ExecutionError(
                str(exc)
            ) from exc

        self.executions.append(
            context.transaction_id
        )

        return result

    def execution_count(
        self,
    ) -> int:
        """
        Return number of executions.
        """

        return len(self.executions)