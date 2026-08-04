"""
Deterministic contract execution engine.

Provides function dispatch, gas metering,
and execution isolation for smart contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .abi import ContractABI
from .context import ExecutionContext
from .contract import Contract
from .events import ContractEvent, EventEmitter
from .exceptions import ContractExecutionError, GasExhaustedError
from .gas import GasMeter
from .storage import ContractStorage


@dataclass(slots=True)
class FunctionHandler:
    """
    Registered handler for a contract function.
    """

    name: str
    handler: Callable[..., Any]
    gas_cost: int = 10


@dataclass(slots=True)
class ContractEngine:
    """
    Deterministic contract execution engine.

    Manages function dispatch, gas metering,
    and execution isolation for deployed contracts.
    """

    _handlers: dict[str, dict[str, FunctionHandler]] = field(
        default_factory=dict,
    )

    def register_handler(
        self,
        contract_id: str,
        handler: FunctionHandler,
    ) -> None:
        """
        Register a function handler for a contract.
        """

        if contract_id not in self._handlers:
            self._handlers[contract_id] = {}

        self._handlers[contract_id][handler.name] = handler

    def get_handler(
        self,
        contract_id: str,
        function_name: str,
    ) -> FunctionHandler:
        """
        Get a registered function handler.
        """

        contract_handlers = self._handlers.get(contract_id)

        if contract_handlers is None:
            raise ContractExecutionError(
                f"No handlers registered for contract '{contract_id}'."
            )

        handler = contract_handlers.get(function_name)

        if handler is None:
            raise ContractExecutionError(
                f"Function '{function_name}' not found on contract '{contract_id}'."
            )

        return handler

    def dispatch(
        self,
        contract: Contract,
        function_name: str,
        context: ExecutionContext,
        storage: ContractStorage,
        gas_meter: GasMeter,
        events: EventEmitter,
        abi: ContractABI,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> Any:
        """
        Dispatch a function call with gas metering and execution isolation.
        """

        handler = self.get_handler(
            contract.contract_id,
            function_name,
        )

        # Consume gas for the function call
        gas_meter.consume(handler.gas_cost)

        if gas_meter.exhausted():
            raise GasExhaustedError(
                f"Gas exhausted during '{function_name}' execution."
            )

        # Build execution payload
        exec_args = args or ()
        exec_kwargs = kwargs or {}

        # Inject runtime dependencies
        exec_kwargs.setdefault("_context", context)
        exec_kwargs.setdefault("_storage", storage)
        exec_kwargs.setdefault("_gas", gas_meter)
        exec_kwargs.setdefault("_events", events)
        exec_kwargs.setdefault("_abi", abi)

        try:
            result = handler.handler(*exec_args, **exec_kwargs)

        except GasExhaustedError:
            raise

        except Exception as exc:
            raise ContractExecutionError(
                f"Execution failed for '{function_name}': {exc}"
            ) from exc

        # Emit execution event
        events.emit(
            ContractEvent(
                event_name="function_executed",
                contract_id=contract.contract_id,
                payload={
                    "function": function_name,
                    "caller": context.caller,
                    "block_height": context.block_height,
                },
            )
        )

        return result

    def has_handler(
        self,
        contract_id: str,
        function_name: str,
    ) -> bool:
        """
        Check if a handler is registered.
        """

        contract_handlers = self._handlers.get(contract_id)

        if contract_handlers is None:
            return False

        return function_name in contract_handlers

    def registered_count(
        self,
        contract_id: str | None = None,
    ) -> int:
        """
        Return number of registered handlers.
        """

        if contract_id is not None:
            return len(self._handlers.get(contract_id, {}))

        return sum(
            len(handlers)
            for handlers in self._handlers.values()
        )

    def clear_handlers(
        self,
        contract_id: str | None = None,
    ) -> None:
        """
        Clear registered handlers.
        """

        if contract_id is not None:
            self._handlers.pop(contract_id, None)
        else:
            self._handlers.clear()
