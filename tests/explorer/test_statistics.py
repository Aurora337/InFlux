from influx.explorer.statistics import (
    ExplorerStatistics,
)


def test_statistics_creation() -> None:
    stats = ExplorerStatistics(
        block_count=10,
        transaction_count=100,
        account_count=25,
    )

    assert stats.block_count == 10
    assert stats.transaction_count == 100
    assert stats.account_count == 25


def test_total_records() -> None:
    stats = ExplorerStatistics(
        block_count=10,
        transaction_count=100,
        account_count=25,
    )

    assert stats.total_records() == 135