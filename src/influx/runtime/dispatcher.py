from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .context import ExecutionContext
from .executor import RuntimeExecutor
from .events import RuntimeEvent
from .queue import RuntimeTask


class RuntimeDispatcher:
    """
    Runtime event and task dispatcher.

    Routes runtime events to handlers and runtime
    tasks into the execution pipeline.
    """

    def __init__(self) -> None:
        self.handlers: dict[
            str,
            Callable[[Any], Any],
        ] = {}

        self.dispatched: int = 0

    def register(
        self,
        event_type: str,
        handler: Callable[[Any], Any],
    ) -> None:
        """
        Register an event handler.
        """

        self.handlers[event_type] = handler

    def dispatch(
        self,
        event: RuntimeEvent | RuntimeTask,
        executor: RuntimeExecutor | None = None,
    ) -> Any:
        """
        Dispatch an event or runtime task.
        """

        self.dispatched += 1

        if isinstance(event, RuntimeEvent):
            handler = self.handlers.get(
                event.event_type,
            )

            if handler is None:
                return 0

            handler(event)

            return 1

        if isinstance(event, RuntimeTask):
            if executor is None:
                return 0

            context = ExecutionContext(
                transaction_id=event.task_id,
                caller="runtime",
                payload=event.payload,
            )

            def operation(
                ctx: ExecutionContext,
            ) -> Any:
                return ctx.payload

            return executor.execute(
                context,
                operation,
            )

        return 0