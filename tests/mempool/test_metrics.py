from influx.mempool.transaction_metrics import (
    TransactionMetrics,
)


def test_received():

    metrics = TransactionMetrics()

    metrics.record_received()

    assert metrics.transactions_received == 1


def test_validated():

    metrics = TransactionMetrics()

    metrics.record_validated()

    assert metrics.transactions_validated == 1


def test_rejected():

    metrics = TransactionMetrics()

    metrics.record_rejected()

    assert metrics.transactions_rejected == 1


def test_scheduled():

    metrics = TransactionMetrics()

    metrics.record_scheduled()

    assert metrics.transactions_scheduled == 1


def test_executed():

    metrics = TransactionMetrics()

    metrics.record_executed()

    assert metrics.transactions_executed == 1


def test_duplicate():

    metrics = TransactionMetrics()

    metrics.record_duplicate()

    assert metrics.duplicates_detected == 1


def test_average_fee():

    metrics = TransactionMetrics()

    metrics.update_average_fee(
        10
    )

    metrics.update_average_fee(
        20
    )

    assert metrics.average_fee == 15


def test_snapshot():

    metrics = TransactionMetrics()

    snapshot = metrics.snapshot()

    assert "transactions_received" in snapshot
    assert "average_fee" in snapshot