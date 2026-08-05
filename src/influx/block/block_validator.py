from __future__ import annotations

from .block import Block


class BlockValidator:
    """
    Validates deterministic blocks.
    """

    def validate_header(
        self,
        block: Block,
    ) -> bool:
        """
        Validate block header.
        """

        header = block.header

        if header.height < 0:
            return False

        if not header.proposer:
            return False

        if not header.previous_hash:
            return False

        return True

    def validate_transactions(
        self,
        block: Block,
    ) -> bool:
        """
        Validate block transaction list.
        """

        return isinstance(
            block.transactions,
            list,
        )

    def validate(
        self,
        block: Block,
    ) -> bool:
        """
        Complete validation.
        """

        return (
            self.validate_header(block)
            and self.validate_transactions(block)
        )