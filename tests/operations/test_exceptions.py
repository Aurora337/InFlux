from influx.operations.exceptions import (
    AlertError,
    HealthError,
    MonitoringError,
    OperationsError,
)


def test_exception_hierarchy() -> None:
    assert issubclass(AlertError, OperationsError)
    assert issubclass(HealthError, OperationsError)
    assert issubclass(MonitoringError, OperationsError)


def test_exception_message() -> None:
    error = OperationsError("failure")
    assert str(error) == "failure"