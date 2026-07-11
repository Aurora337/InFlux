from __future__ import annotations

from dataclasses import dataclass

from .blocks import BlockRecord
from .transactions import TransactionRecord
from .accounts import AccountRecord


@dataclass(frozen=True, slots=True)
class BlockQueryResult:
    """
    Block query response.
    """

    block: BlockRecord


@dataclass(frozen=True, slots=True)
class TransactionQueryResult:
    """
    Transaction query response.
    """

    transaction: TransactionRecord


@dataclass(frozen=True, slots=True)
class AccountQueryResult:
    """
    Account query response.
    """

    account: AccountRecord