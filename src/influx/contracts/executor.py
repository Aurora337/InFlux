from __future__ import annotations

from dataclasses import dataclass

from .context import ExecutionContext
from .contract import Contract
from .exceptions import ContractExecutionError
from .storage import ContractStorage


@dataclass(slots=True)
class ExecutionResult:
    """
    Result of deterministic execution.
    """

    success: bool
    contract_id: str
    message: str


class ContractExecutor:
    """
    Deterministic smart contract executor.
    """

    def execute(
        self,
        contract: Contract,
        context: ExecutionContext,
        storage: ContractStorage,
    ) -> ExecutionResult:
        """
        Execute a contract.
        """

        if not contract.contract_id:
            raise ContractExecutionError(
                "Invalid contract identifier."
            )

        storage.put(
            "last_transaction",
            context.transaction_id,
        )

        storage.put(
            "last_caller",
            context.caller,
        )

        storage.put(
            "last_block",
            str(context.block_height),
        )

        return ExecutionResult(
            success=True,
            contract_id=contract.contract_id,
            message="Execution completed.",
        )