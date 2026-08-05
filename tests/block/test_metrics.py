from influx.block.block_metrics import (
    BlockMetrics,
)


def test_created():

    metrics = BlockMetrics()

    metrics.record_created()

    assert metrics.blocks_created == 1


def test_validated():

    metrics = BlockMetrics()

    metrics.record_validated()

    assert metrics.blocks_validated == 1


def test_rejected():

    metrics = BlockMetrics()

    metrics.record_rejected()

    assert metrics.blocks_rejected == 1


def test_committed():

    metrics = BlockMetrics()

    metrics.record_committed()

    assert metrics.blocks_committed == 1


def test_transactions():

    metrics = BlockMetrics()

    metrics.record_transactions(10)

    assert metrics.transactions_included == 10


def test_validation_failure():

    metrics = BlockMetrics()

    metrics.record_validation_failure()

    assert metrics.validation_failures == 1


def test_build_time():

    metrics = BlockMetrics()

    metrics.update_build_time(10)

    metrics.update_build_time(20)

    assert metrics.average_build_time == 15


def test_snapshot():

    metrics = BlockMetrics()

    snapshot = metrics.snapshot()

    assert "blocks_created" in snapshot
    assert "average_build_time" in snapshot