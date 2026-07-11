from influx.explorer.exceptions import (
    ExplorerError,
    IndexingError,
    QueryError,
    RecordNotFoundError,
)


def test_exception_hierarchy() -> None:
    assert issubclass(IndexingError, ExplorerError)
    assert issubclass(QueryError, ExplorerError)
    assert issubclass(RecordNotFoundError, QueryError)


def test_exception_messages() -> None:
    error = ExplorerError("explorer error")

    assert str(error) == "explorer error"