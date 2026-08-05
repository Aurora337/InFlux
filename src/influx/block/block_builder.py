from __future__ import annotations

from time import time

from .block import Block
from .block_header import BlockHeader
from .block_scheduler import BlockScheduler


class BlockBuilder:
    """
    Builds deterministic blocks.
    """

    def __init__(
        self,
        proposer: str,
        max_transactions: int = 1000,
    ) -> None:

        self.proposer = proposer

        self.max_transactions = (
            max_transactions
        )

    def build(
        self,
        transactions: list,
        previous_hash: str,
        height: int,
        state_root: str = "",
    ) -> Block:
        """
        Construct a block candidate.
        """

        selected = (
            BlockScheduler.select(
                transactions,
                self.max_transactions,
            )
        )

        header = BlockHeader(
            height=height,
            previous_hash=previous_hash,
            block_hash="",
            transaction_root="",
            state_root=state_root,
            timestamp=time(),
            proposer=self.proposer,
        )

        return Block(
            header=header,
            transactions=selected,
        )