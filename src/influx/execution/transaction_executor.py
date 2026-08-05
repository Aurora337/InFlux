from __future__ import annotations

from .execution_result import ExecutionResult
from .state_machine import StateMachine


class TransactionExecutor:
    """
    Executes individual transactions
    against the deterministic state machine.
    """

    def __init__(
        self,
        state_machine: StateMachine,
    ) -> None:

        self.state_machine = state_machine

    def execute(
        self,
        transaction,
    ) -> ExecutionResult:
        """
        Execute a deterministic transaction.
        """

        try:
            sender = transaction.sender
            receiver = transaction.receiver
            amount = transaction.amount

            sender_balance = (
                self.state_machine.get(sender)
                or 0
            )

            receiver_balance = (
                self.state_machine.get(receiver)
                or 0
            )

            changes = {
                sender:
                    sender_balance - amount,

                receiver:
                    receiver_balance + amount,
            }

            self.state_machine.apply_changes(
                changes
            )

            return ExecutionResult(
                success=True,
                transaction_id=transaction.transaction_id,
                state_changes=changes,
            )

        except Exception as error:

            return ExecutionResult(
                success=False,
                transaction_id=getattr(
                    transaction,
                    "transaction_id",
                    "",
                ),
                error=str(error),
            )