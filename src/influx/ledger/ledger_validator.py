from __future__ import annotations

from .ledger import Ledger


class LedgerValidator:
    """
    Validates ledger consistency.
    """

    def validate_height(
        self,
        ledger: Ledger,
    ) -> bool:
        """
        Verify height matches blocks.
        """

        return (
            ledger.state.height
            == len(ledger.blocks)
        )

    def validate_chain(
        self,
        ledger: Ledger,
    ) -> bool:
        """
        Verify block continuity.
        """

        if not ledger.blocks:
            return True

        previous = None

        for block in ledger.blocks:

            if previous is not None:

                if (
                    block.header.previous_hash
                    != previous.header.block_hash
                ):
                    return False

            previous = block

        return True

    def validate_state(
        self,
        ledger: Ledger,
    ) -> bool:
        """
        Validate state availability.
        """

        return (
            ledger.state is not None
        )

    def validate(
        self,
        ledger: Ledger,
    ) -> bool:
        """
        Complete ledger validation.
        """

        return (
            self.validate_height(ledger)
            and self.validate_chain(ledger)
            and self.validate_state(ledger)
        )