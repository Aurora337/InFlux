from influx.ledger.ledger_metrics import (
    LedgerMetrics,
)


def test_block_commit():

    metrics = LedgerMetrics()

    metrics.record_block_commit()

    assert (
        metrics.blocks_committed
        == 1
    )


def test_transaction_record():

    metrics = LedgerMetrics()

    metrics.record_transaction(
        5
    )

    assert (
        metrics.transactions_applied
        == 5
    )


def test_state_update():

    metrics = LedgerMetrics()

    metrics.record_state_update()

    assert (
        metrics.state_updates
        == 1
    )


def test_validation_failure():

    metrics = LedgerMetrics()

    metrics.record_validation_failure()

    assert (
        metrics.validation_failures
        == 1
    )


def test_commit_failure():

    metrics = LedgerMetrics()

    metrics.record_commit_failure()

    assert (
        metrics.commit_failures
        == 1
    )


def test_commit_time():

    metrics = LedgerMetrics()

    metrics.update_commit_time(
        10
    )

    metrics.update_commit_time(
        20
    )

    assert (
        metrics.average_commit_time
        == 15
    )


def test_snapshot():

    metrics = LedgerMetrics()

    snapshot = metrics.snapshot()

    assert (
        "blocks_committed"
        in snapshot
    )

    assert (
        "average_commit_time"
        in snapshot
    )