from __future__ import annotations

from .ledger_state import LedgerState


class StateTransition:
    """
    Applies deterministic state changes.
    """

    def apply(
        self,
        state: LedgerState,
        transaction,
    ) -> LedgerState:
        """
        Apply a transaction to state.
        """

        sender = transaction.sender

        receiver = transaction.receiver

        amount = transaction.amount

        sender_balance = (
            state.get_account(sender)
            or 0
        )

        receiver_balance = (
            state.get_account(receiver)
            or 0
        )

        state.update_account(
            sender,
            sender_balance - amount,
        )

        state.update_account(
            receiver,
            receiver_balance + amount,
        )

        return state