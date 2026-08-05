from __future__ import annotations

from .ledger import Ledger
from .state_transition import StateTransition


class CommitEngine:
    """
    Applies finalized blocks to the ledger.
    """

    def __init__(
        self,
        ledger: Ledger,
        transition: StateTransition | None = None,
    ) -> None:

        self.ledger = ledger

        self.transition = (
            transition
            if transition is not None
            else StateTransition()
        )

    def apply_transactions(
        self,
        block,
    ) -> None:
        """
        Apply all block transactions.
        """

        for transaction in block.transactions:

            self.transition.apply(
                self.ledger.state,
                transaction,
            )

    def commit(
        self,
        block,
    ) -> bool:
        """
        Commit finalized block.
        """

        self.apply_transactions(
            block
        )

        self.ledger.append_block(
            block
        )

        return True

    def snapshot(
        self,
    ) -> dict:
        """
        Return commit state snapshot.
        """

        return self.ledger.snapshot()