from __future__ import annotations

from .state_machine import (
    StateMachine,
)

from .transaction_executor import (
    TransactionExecutor,
)


class ExecutionEngine:
    """
    Coordinates deterministic execution
    of blocks and transactions.
    """

    def __init__(
        self,
        state_machine: StateMachine | None = None,
    ) -> None:

        self.state_machine = (
            state_machine
            if state_machine is not None
            else StateMachine()
        )

        self.executor = (
            TransactionExecutor(
                self.state_machine
            )
        )

    def execute_transaction(
        self,
        transaction,
    ):
        """
        Execute one transaction.
        """

        return self.executor.execute(
            transaction
        )

    def execute_block(
        self,
        block,
    ) -> list:
        """
        Execute every transaction
        in a block.
        """

        results = []

        for transaction in block.transactions:

            result = (
                self.execute_transaction(
                    transaction
                )
            )

            results.append(
                result
            )

        return results

    def snapshot(
        self,
    ) -> dict:
        """
        Return execution state.
        """

        return self.state_machine.snapshot()