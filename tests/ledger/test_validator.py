from influx.ledger.ledger import Ledger
from influx.ledger.ledger_validator import (
    LedgerValidator,
)


class Header:

    def __init__(
        self,
        previous_hash,
        block_hash,
    ):
        self.previous_hash = previous_hash
        self.block_hash = block_hash


class Block:

    def __init__(
        self,
        previous_hash,
        block_hash,
    ):
        self.header = Header(
            previous_hash,
            block_hash,
        )


def test_empty_chain_valid():

    ledger = Ledger()

    validator = LedgerValidator()

    assert validator.validate(
        ledger
    )


def test_height_validation():

    ledger = Ledger()

    validator = LedgerValidator()

    assert validator.validate_height(
        ledger
    )


def test_valid_chain():

    ledger = Ledger()

    ledger.blocks = [
        Block(
            "genesis",
            "block-1",
        ),
        Block(
            "block-1",
            "block-2",
        ),
    ]

    ledger.state.height = 2

    validator = LedgerValidator()

    assert validator.validate_chain(
        ledger
    )


def test_invalid_chain():

    ledger = Ledger()

    ledger.blocks = [
        Block(
            "wrong",
            "block-2",
        ),
        Block(
            "block-1",
            "block-3",
        ),
    ]

    validator = LedgerValidator()

    assert not validator.validate_chain(
        ledger
    )