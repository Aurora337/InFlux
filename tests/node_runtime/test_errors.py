from influx.node_runtime.errors import (
    NodeRuntimeError,
    NodeConfigurationError,
    NodeIdentityError,
    NodeHealthError,
    NodeLifecycleError,
)


def test_error_hierarchy() -> None:
    assert issubclass(
        NodeConfigurationError,
        NodeRuntimeError,
    )

    assert issubclass(
        NodeIdentityError,
        NodeRuntimeError,
    )

    assert issubclass(
        NodeHealthError,
        NodeRuntimeError,
    )

    assert issubclass(
        NodeLifecycleError,
        NodeRuntimeError,
    )