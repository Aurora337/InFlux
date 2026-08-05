from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Any

from .block_header import BlockHeader
from .block_state import BlockState


@dataclass(slots=True)
class Block:
    """
    Represents a deterministic InFlux block.
    """

    header: BlockHeader

    transactions: list[Any]

    created_at: float = field(
        default_factory=time
    )

    state: BlockState = (
        BlockState.CREATED
    )

    def start_building(self) -> None:
        """
        Begin block construction.
        """

        self.state = (
            BlockState.BUILDING
        )

    def seal(self) -> None:
        """
        Seal block contents.
        """

        self.state = (
            BlockState.SEALED
        )

    def validate(self) -> None:
        """
        Begin validation.
        """

        self.state = (
            BlockState.VALIDATING
        )

    def mark_valid(self) -> None:
        """
        Mark block valid.
        """

        self.state = (
            BlockState.VALID
        )

    def commit(self) -> None:
        """
        Commit block.
        """

        self.state = (
            BlockState.COMMITTED
        )

    def reject(self) -> None:
        """
        Reject block.
        """

        self.state = (
            BlockState.INVALID
        )

    def snapshot(self) -> dict:
        """
        Deterministic block snapshot.
        """

        return {
            "header":
                self.header.snapshot(),

            "transactions":
                [
                    tx.snapshot()
                    if hasattr(tx, "snapshot")
                    else tx
                    for tx in self.transactions
                ],

            "created_at":
                self.created_at,

            "state":
                self.state.value,
        }