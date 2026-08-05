from influx.mempool.exceptions import (
    MempoolError,
    InvalidTransactionError,
    DuplicateTransactionError,
    TransactionNotFoundError,
)


def test_exception_hierarchy():

    assert issubclass(
        InvalidTransactionError,
        MempoolError,
    )

    assert issubclass(
        DuplicateTransactionError,
        MempoolError,
    )

    assert issubclass(
        TransactionNotFoundError,
        MempoolError,
    )