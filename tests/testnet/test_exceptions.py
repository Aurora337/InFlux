from influx.testnet.exceptions import (
    TestnetError,
    NodeError,
    NetworkError,
    SimulationError,
)


def test_exception_hierarchy() -> None:
    assert issubclass(NodeError, TestnetError)
    assert issubclass(NetworkError, TestnetError)
    assert issubclass(SimulationError, TestnetError)


def test_exception_message() -> None:
    error = TestnetError("failure")

    assert str(error) == "failure"