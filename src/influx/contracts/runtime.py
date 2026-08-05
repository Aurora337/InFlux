from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .abi import ContractABI
from .call import CallStack, CallContext
from .contract import Contract
from .context import ExecutionContext
from .engine import ContractEngine, FunctionHandler
from .events import ContractEvent, EventEmitter
from .exceptions import (
    ContractError,
    ContractExecutionError,
    ContractRegistrationError,
    GasExhaustedError,
)
from .executor import ExecutionResult
from .gas import GasMeter
from .registry import ContractRegistry
from .storage import ContractStorage


@dataclass(slots=True)
class ContractRuntime:
    """
    Deterministic smart contract runtime with lifecycle management.
    """

    contracts: dict[str, Contract] = field(
        default_factory=dict,
    )

    contract_storage: dict[str, ContractStorage] = field(
        default_factory=dict,
    )

    engine: ContractEngine = field(
        default_factory=ContractEngine,
    )

    registry: ContractRegistry = field(
        default_factory=ContractRegistry,
    )

    call_stack: CallStack = field(
        default_factory=CallStack,
    )

    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------

    def register(
        self,
        contract: Contract,
    ) -> None:
        """
        Register a contract.
        """

        if contract.contract_id in self.contracts:
            raise ContractRegistrationError(
                f"Contract '{contract.contract_id}' already registered."
            )

        self.contracts[contract.contract_id] = contract

        self.registry.register(
            contract.contract_id,
            {
                "owner": contract.owner,
                "version": contract.version,
                "code_hash": contract.code_hash,
            },
        )

    def register_handler(
        self,
        contract_id: str,
        handler: FunctionHandler,
    ) -> None:
        """
        Register an executable handler.
        """

        self.engine.register_handler(
            contract_id,
            handler,
        )

    # ---------------------------------------------------------
    # Queries
    # ---------------------------------------------------------

    def get(
        self,
        contract_id: str,
    ) -> Contract:
        if contract_id not in self.contracts:
            raise ContractError(
                f"Contract '{contract_id}' not found."
            )

        return self.contracts[contract_id]

    def has_contract(
        self,
        contract_id: str,
    ) -> bool:
        return contract_id in self.contracts

    def has_handler(
        self,
        contract_id: str,
        function_name: str,
    ) -> bool:
        return self.engine.has_handler(
            contract_id,
            function_name,
        )

    def registered(self) -> int:
        return len(self.contracts)

    # ---------------------------------------------------------
    # Deployment
    # ---------------------------------------------------------

    def deploy(
        self,
        contract: Contract,
        context: ExecutionContext,
        storage: ContractStorage,
        gas_meter: GasMeter,
        events: EventEmitter,
        initial_state: dict[str, str] | None = None,
    ) -> ExecutionResult:
        """
        Deploy a contract and persist its state.

        Deployment performs:
        - contract registration
        - initial storage population
        - deployment metadata creation
        - deployment event emission
        """

        #
        # Register contract if it is not already registered.
        #
        if not self.has_contract(contract.contract_id):
            self.register(contract)

        #
        # Consume deployment gas.
        #
        gas_meter.consume(5)

        if gas_meter.exhausted():
            raise GasExhaustedError(
                "Gas exhausted during contract deployment."
            )

        #
        # Initialize contract storage.
        #
        if initial_state:
            for key, value in initial_state.items():
                storage.put(
                    key,
                    value,
                )

        #
        # Deployment metadata.
        #
        storage.put(
            "deployer",
            context.caller,
        )

        storage.put(
            "deployed_at_block",
            str(context.block_height),
        )

        storage.put(
            "contract_version",
            contract.version,
        )

        #
        # Persist deployed storage.
        #
        self.contract_storage[
            contract.contract_id
        ] = storage

        events.emit(
            ContractEvent(
                event_name="contract_deployed",
                contract_id=contract.contract_id,
                payload={
                    "owner": contract.owner,
                    "version": contract.version,
                    "code_hash": contract.code_hash,
                    "deployer": context.caller,
                    "block_height": context.block_height,
                },
            )
        )

        return ExecutionResult(
            success=True,
            contract_id=contract.contract_id,
            message="Deployment completed.",
        )

    # ---------------------------------------------------------
    # Execution
    # ---------------------------------------------------------

    def execute(
        self,
        contract_id: str,
        function_name: str,
        context: ExecutionContext,
        storage: ContractStorage,
        gas_meter: GasMeter,
        abi: ContractABI,
        events: EventEmitter,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> Any:
        """
        Execute a contract function deterministically.
        """

        contract = self.get(contract_id)

        storage = self._get_storage(
            contract_id,
            storage,
        )

        self._validate_execution(
            contract_id,
            function_name,
        )

        self._push_call(
            context,
            contract_id,
            function_name,
            gas_meter,
        )

        try:
            return self.engine.dispatch(
                contract=contract,
                function_name=function_name,
                context=context,
                storage=storage,
                gas_meter=gas_meter,
                events=events,
                abi=abi,
                args=args,
                kwargs=kwargs,
            )

        finally:
            self._pop_call()

    # ---------------------------------------------------------
    # Cross-contract calls
    # ---------------------------------------------------------

    def call(
        self,
        target_contract_id: str,
        function_name: str,
        caller: str,
        context: ExecutionContext,
        storage: ContractStorage,
        gas_meter: GasMeter,
        abi: ContractABI,
        events: EventEmitter,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> Any:

        if self.call_stack.is_reentrant(
            target_contract_id,
            function_name,
        ):
            raise ContractExecutionError(
                "Reentrant contract call detected."
            )

        if not self.engine.has_handler(
            target_contract_id,
            function_name,
        ):
            raise ContractExecutionError(
                f"Function '{function_name}' not registered "
                f"for contract '{target_contract_id}'."
            )

        call_context = ExecutionContext(
            network_id=context.network_id,
            block_height=context.block_height,
            transaction_id=context.transaction_id,
            caller=caller,
        )

        return self.execute(
            contract_id=target_contract_id,
            function_name=function_name,
            context=call_context,
            storage=storage,
            gas_meter=gas_meter,
            abi=abi,
            events=events,
            args=args,
            kwargs=kwargs,
        )

        # ---------------------------------------------------------
    # Internal Helpers
    # ---------------------------------------------------------

    def _get_storage(
        self,
        contract_id: str,
        storage: ContractStorage,
    ) -> ContractStorage:
        """
        Return deployed storage when available.
        """

        return self.contract_storage.get(
            contract_id,
            storage,
        )

    def _validate_execution(
        self,
        contract_id: str,
        function_name: str,
    ) -> None:
        """
        Validate execution state before dispatch.
        """

        if not self.engine.has_handler(
            contract_id,
            function_name,
        ):
            raise ContractExecutionError(
                f"Function '{function_name}' not registered "
                f"for contract '{contract_id}'."
            )

        if self.call_stack.is_reentrant(
            contract_id,
            function_name,
        ):
            raise ContractExecutionError(
                "Reentrant contract call detected."
            )

    def _push_call(
        self,
        context: ExecutionContext,
        contract_id: str,
        function_name: str,
        gas_meter: GasMeter,
    ) -> None:
        """
        Push a call onto the deterministic call stack.
        """

        self.call_stack.push(
            CallContext(
                caller=context.caller,
                contract_id=contract_id,
                function=function_name,
                gas_limit=gas_meter.limit,
            )
        )

    def _pop_call(self) -> None:
        """
        Pop the active call from the deterministic call stack.
        """

        self.call_stack.pop()

    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------

    def get_registry(self) -> ContractRegistry:
        return self.registry

    def get_call_chain(self) -> list[dict[str, Any]]:
        return self.call_stack.call_chain()

    def reset(self) -> None:
        """
        Reset runtime state.
        """

        self.contracts.clear()
        self.contract_storage.clear()
        self.engine.clear_handlers()
        self.registry = ContractRegistry()
        self.call_stack.reset()