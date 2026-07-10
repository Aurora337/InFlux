from influx.block.block import Block
from influx.block.block_header import BlockHeader
from influx.block.block_state import BlockState


def create_header():

    return BlockHeader(
        height=1,
        previous_hash="previous",
        block_hash="hash",
        transaction_root="tx-root",
        state_root="state-root",
        timestamp=100.0,
        proposer="node-a",
    )


def create_block():

    return Block(
        header=create_header(),
        transactions=[],
    )


def test_header_snapshot():

    header = create_header()

    snapshot = header.snapshot()

    assert snapshot["height"] == 1
    assert snapshot["previous_hash"] == "previous"
    assert snapshot["block_hash"] == "hash"
    assert snapshot["proposer"] == "node-a"


def test_block_defaults():

    block = create_block()

    assert (
        block.state
        == BlockState.CREATED
    )


def test_start_building():

    block = create_block()

    block.start_building()

    assert (
        block.state
        == BlockState.BUILDING
    )


def test_seal():

    block = create_block()

    block.seal()

    assert (
        block.state
        == BlockState.SEALED
    )


def test_validate():

    block = create_block()

    block.validate()

    assert (
        block.state
        == BlockState.VALIDATING
    )


def test_mark_valid():

    block = create_block()

    block.mark_valid()

    assert (
        block.state
        == BlockState.VALID
    )


def test_commit():

    block = create_block()

    block.commit()

    assert (
        block.state
        == BlockState.COMMITTED
    )


def test_reject():

    block = create_block()

    block.reject()

    assert (
        block.state
        == BlockState.INVALID
    )


def test_snapshot():

    block = create_block()

    snapshot = block.snapshot()

    assert "header" in snapshot
    assert "transactions" in snapshot
    assert snapshot["state"] == "created"