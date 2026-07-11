from influx.contracts.exceptions import (
    ContractError,
    ContractExecutionError,
    ContractRegistrationError,
    GasExhaustedError,
)


def test_exception_hierarchy() -> None:
    assert issubclass(ContractExecutionError, ContractError)
    assert issubclass(ContractRegistrationError, ContractError)
    assert issubclass(GasExhaustedError, ContractError)


def test_exception_message() -> None:
    error = ContractError("runtime failure")
    assert str(error) == "runtime failure"