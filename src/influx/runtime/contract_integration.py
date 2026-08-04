"""
Bridge between Runtime and Contract modules.

Integrates the smart contract runtime into the
main InFlux node runtime pipeline.

Provides:
- ContractRuntimeCoordinator adapter
- Task-to-contract execution mapping
- Lifecycle hooks for contract operations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from ..contracts import (
    Contract,
    ContractRuntime,
    ContractABI,
    EventEmitter,
    ExecutionContext as ContractExecutionContext,
    ContractStorage,
    ExecutionResult,
    GasMeter,
    GasExhaustedError,
    ContractError,
)
from ..contracts.engine import FunctionHandler
from .context import ExecutionContext as RuntimeExecutionContext
from .executor import RuntimeExecutor
from .queue import RuntimeTask
from .transition import ExecutionReceipt


@dataclass(slots=True)
class ContractRuntimeCoordinator:
    """
    Coordinates contract execution within the runtime pipeline.

    Adapts the ContractRuntime to work with the
    existing RuntimeCoordinator infrastructure.
    """

    contract_runtime: ContractRuntime = field(
        default_factory=ContractRuntime,
    )
    default_gas_limit: int = 100_000

    def create_contract_context(
        self,
        runtime_context: RuntimeExecutionContext,
        network_id: str = "influx-mainnet",
    ) -> ContractExecutionContext:
        """
        Create a contract execution context from a runtime context.
        """

        return ContractExecutionContext(
            block_height=0,
            transaction_id=runtime_context.transaction_id or "",
            caller="",
            network_id=network_id,
        )

    def deploy_contract(
        self,
        contract: Contract,
        runtime_context: RuntimeExecutionContext,
        network_id: str = "influx-mainnet",
        initial_state: dict[str, str] | None = None,
    ) -> ExecutionResult:
        """
        Deploy a contract within the runtime context.
        """

        contract_ctx = self.create_contract_context(
            runtime_context,
            network_id,
        )

        storage = ContractStorage()
        gas_meter = GasMeter(limit=self.default_gas_limit)
        events = EventEmitter()

        result = self.contract_runtime.deploy(
            contract=contract,
            context=contract_ctx,
            storage=storage,
            gas_meter=gas_meter,
            events=events,
            initial_state=initial_state,
        )

        return result

    def execute_contract(
        self,
        contract_id: str,
        function_name: str,
        runtime_context: RuntimeExecutionContext,
        network_id: str = "influx-mainnet",
        storage: ContractStorage | None = None,
        gas_limit: int | None = None,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> Any:
        """
        Execute a contract function within the runtime context.
        """

        contract_ctx = self.create_contract_context(
            runtime_context,
            network_id,
        )

        contract_storage = storage or ContractStorage()
        gas_meter = GasMeter(limit=gas_limit or self.default_gas_limit)
        events = EventEmitter()
        abi = ContractABI()

        result = self.contract_runtime.execute(
            contract_id=contract_id,
            function_name=function_name,
            context=contract_ctx,
            storage=contract_storage,
            gas_meter=gas_meter,
            abi=abi,
            events=events,
            args=args,
            kwargs=kwargs,
        )

        return result

    def register_contract(
        self,
        contract: Contract,
        handlers: list[tuple[str, Callable[..., Any], int]] | None = None,
    ) -> None:
        """
        Register a contract with optional function handlers.
        """

        self.contract_runtime.register(contract)

        if handlers:
            for handler_name, handler_fn, gas_cost in handlers:
                self.contract_runtime.register_handler(
                    contract.contract_id,
                    FunctionHandler(
                        name=handler_name,
                        handler=handler_fn,
                        gas_cost=gas_cost,
                    ),
                )

    def contract_count(self) -> int:
        """
        Return number of registered contracts.

        Compatibility alias for runtime integrations.
        """

        return self.contract_runtime.registered()

    def registered_contracts(self) -> int:
        """
        Return number of registered contracts.

        Compatibility alias used by integration tests.
        """

        return self.contract_runtime.registered()   

    def register_handler(
        self,
        contract_id: str,
        handler: FunctionHandler,
    ) -> None:
        """
        Register a function handler for a contract.

        Adapter method exposing ContractRuntime handler registration.
        """

        self.contract_runtime.register_handler(
            contract_id,
            handler,
        )

    def process_contract_task(
        self,
        task: RuntimeTask,
        runtime_executor: RuntimeExecutor,
    ) -> ExecutionReceipt:
        """
        Process a runtime task that targets a contract.

        Expected task payload:
        {
            "contract_id": str,
            "function": str,
            "args": tuple,
            "kwargs": dict,
            "gas_limit": int (optional),
        }
        """

        payload = task.payload

        contract_id = payload.get("contract_id", "")
        function_name = payload.get("function", "")
        args = payload.get("args", ())
        kwargs = payload.get("kwargs", {})
        gas_limit = payload.get("gas_limit", self.default_gas_limit)

        runtime_ctx = RuntimeExecutionContext(
            transaction_id=task.task_id,
            caller="",
        )

        try:
            result = self.execute_contract(
                contract_id=contract_id,
                function_name=function_name,
                runtime_context=runtime_ctx,
                gas_limit=gas_limit,
                args=args,
                kwargs=kwargs,
            )

            return ExecutionReceipt(
                transaction_id=task.task_id,
                success=True,
                changes={"result": str(result)},
            )

        except (ContractError, GasExhaustedError) as exc:
            return ExecutionReceipt(
                transaction_id=task.task_id,
                success=False,
                changes={"error": str(exc)},
            )

    def registered_count(self) -> int:
        """
        Return number of registered contracts.
        """

        return self.contract_runtime.registered()

    def has_contract(self, contract_id: str) -> bool:
        """
        Check if a contract is registered.
        """

        return self.contract_runtime.has_contract(contract_id)

    def get_runtime(self) -> ContractRuntime:
        """
        Get the underlying contract runtime.
        """

        return self.contract_runtime
