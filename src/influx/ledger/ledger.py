from __future__ import annotations

from .ledger_state import LedgerState


class Ledger:
    """
    Canonical deterministic ledger.
    """

    def __init__(
        self,
        state: LedgerState | None = None,
    ) -> None:

        self.state = (
            state
            if state is not None
            else LedgerState()
        )

        self.blocks: list = []

    def height(
        self,
    ) -> int:
        return self.state.height

    def append_block(
        self,
        block,
    ) -> None:
        """
        Append finalized block.
        """

        self.blocks.append(
            block
        )

        self.state.height += 1

    def latest_block(
        self,
    ):
        if not self.blocks:
            return None

        return self.blocks[-1]

    def snapshot(
        self,
    ) -> dict:
        """
        Ledger snapshot.
        """

        return {
            "state":
                self.state.snapshot(),

            "blocks":
                len(self.blocks),
        }