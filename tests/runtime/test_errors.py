from influx.runtime.errors import (
    ContextError,
    ExecutionError,
    RuntimeErrorBase,
    StateTransitionError,
)


def test_runtime_errors_inherit_base() -> None:
    assert issubclass(
        ExecutionError,
        RuntimeErrorBase,
    )

    assert issubclass(
        ContextError,
        RuntimeErrorBase,
    )

    assert issubclass(
        StateTransitionError,
        RuntimeErrorBase,
    )