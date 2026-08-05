from __future__ import annotations

from dataclasses import dataclass, field

from .blocks import BlockRecord
from .transactions import TransactionRecord
from .accounts import AccountRecord
from .exceptions import (
    IndexingError,
)


@dataclass(slots=True)
class ExplorerIndexer:
    """
    Deterministic explorer indexing engine.
    """

    blocks: dict[int, BlockRecord] = field(
        default_factory=dict,
    )

    transactions: dict[str, TransactionRecord] = field(
        default_factory=dict,
    )

    accounts: dict[str, AccountRecord] = field(
        default_factory=dict,
    )

    def index_block(
        self,
        block: BlockRecord,
    ) -> None:
        """
        Store a block record.
        """

        if block.height < 0:
            raise IndexingError(
                "invalid block height"
            )

        self.blocks[block.height] = block

    def index_transaction(
        self,
        transaction: TransactionRecord,
    ) -> None:
        """
        Store a transaction record.
        """

        if not transaction.tx_id:
            raise IndexingError(
                "missing transaction id"
            )

        self.transactions[
            transaction.tx_id
        ] = transaction

    def index_account(
        self,
        account: AccountRecord,
    ) -> None:
        """
        Store an account record.
        """

        if not account.address:
            raise IndexingError(
                "missing account address"
            )

        self.accounts[
            account.address
        ] = account

    def block_count(
        self,
    ) -> int:
        """
        Return indexed block count.
        """

        return len(self.blocks)

    def transaction_count(
        self,
    ) -> int:
        """
        Return indexed transaction count.
        """

        return len(self.transactions)

    def account_count(
        self,
    ) -> int:
        """
        Return indexed account count.
        """

        return len(self.accounts)