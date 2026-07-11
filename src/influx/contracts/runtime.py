from __future__ import annotations

from dataclasses import dataclass, field

from .abi import ContractABI
from .contract import Contract
from .context import ExecutionContext
from .events import EventEmitter
from .executor import ContractExecutor, ExecutionResult
from .exceptions import ContractRegistrationError
from .gas import GasMeter
from .storage import ContractStorage


@dataclass(slots=True)
class ContractRuntime:
    """
    Deterministic smart contract runtime.
    """

    contracts: dict[str, Contract] = field(default_factory=dict)

    def register(
        self,
        contract: Contract,
    ) -> None:
        if contract.contract_id in self.contracts:
            raise ContractRegistrationError(
                f"Contract '{contract.contract_id}' already registered."
            )

        self.contracts[contract.contract_id] = contract

    def get(
        self,
        contract_id: str,
    ) -> Contract:
        return self.contracts[contract_id]

    def registered(self) -> int:
        return len(self.contracts)

    def execute(
        self,
        contract_id: str,
        context: ExecutionContext,
        storage: ContractStorage,
        gas_meter: GasMeter,
        abi: ContractABI,
        events: EventEmitter,
    ) -> ExecutionResult:
        """
        Execute a registered contract.

        ABI and EventEmitter are accepted so every execution
        occurs inside a complete deterministic runtime context.
        """

        contract = self.get(contract_id)

        # Runtime overhead
        gas_meter.consume(1)

        executor = ContractExecutor()

        result = executor.execute(
            contract,
            context,
            storage,
        )

        return result