from influx.explorer.blocks import BlockRecord


def test_block_record_creation() -> None:
    block = BlockRecord(
        height=1,
        block_hash="abc",
        previous_hash="genesis",
        timestamp=1000,
        transaction_ids=["tx1"],
    )

    assert block.height == 1
    assert block.block_hash == "abc"
    assert block.transaction_ids == ["tx1"]