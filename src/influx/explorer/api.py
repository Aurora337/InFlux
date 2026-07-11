from __future__ import annotations

from .indexer import ExplorerIndexer
from .queries import (
    BlockQueryResult,
    TransactionQueryResult,
    AccountQueryResult,
)
from .exceptions import (
    RecordNotFoundError,
)


class ExplorerAPI:
    """
    Public explorer query interface.
    """

    def __init__(
        self,
        indexer: ExplorerIndexer,
    ) -> None:

        self._indexer = indexer

    def get_block(
        self,
        height: int,
    ) -> BlockQueryResult:
        """
        Retrieve a block by height.
        """

        block = self._indexer.blocks.get(
            height
        )

        if block is None:
            raise RecordNotFoundError(
                "block not found"
            )

        return BlockQueryResult(
            block=block,
        )

    def get_transaction(
        self,
        tx_id: str,
    ) -> TransactionQueryResult:
        """
        Retrieve a transaction by id.
        """

        transaction = (
            self._indexer.transactions.get(
                tx_id
            )
        )

        if transaction is None:
            raise RecordNotFoundError(
                "transaction not found"
            )

        return TransactionQueryResult(
            transaction=transaction,
        )

    def get_account(
        self,
        address: str,
    ) -> AccountQueryResult:
        """
        Retrieve an account by address.
        """

        account = (
            self._indexer.accounts.get(
                address
            )
        )

        if account is None:
            raise RecordNotFoundError(
                "account not found"
            )

        return AccountQueryResult(
            account=account,
        )