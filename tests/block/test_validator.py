from influx.block.block import Block
from influx.block.block_header import BlockHeader
from influx.block.block_validator import (
    BlockValidator,
)


def create_block():

    header = BlockHeader(
        height=1,
        previous_hash="previous",
        block_hash="hash",
        transaction_root="tx-root",
        state_root="state-root",
        timestamp=100.0,
        proposer="node-a",
    )

    return Block(
        header=header,
        transactions=[],
    )


def test_valid_header():

    validator = BlockValidator()

    assert validator.validate_header(
        create_block()
    )


def test_invalid_height():

    validator = BlockValidator()

    block = create_block()

    block.header.height = -1

    assert not validator.validate_header(
        block
    )


def test_missing_proposer():

    validator = BlockValidator()

    block = create_block()

    block.header.proposer = ""

    assert not validator.validate_header(
        block
    )


def test_missing_previous_hash():

    validator = BlockValidator()

    block = create_block()

    block.header.previous_hash = ""

    assert not validator.validate_header(
        block
    )


def test_validate_transactions():

    validator = BlockValidator()

    assert validator.validate_transactions(
        create_block()
    )


def test_complete_validation():

    validator = BlockValidator()

    assert validator.validate(
        create_block()
    )