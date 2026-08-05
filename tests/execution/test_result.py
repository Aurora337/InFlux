from influx.execution.execution_result import (
    ExecutionResult,
)


def test_success_result():

    result = ExecutionResult(
        success=True,
        transaction_id="tx-1",
    )

    assert (
        result.success
        is True
    )

    assert (
        result.transaction_id
        == "tx-1"
    )


def test_failed_result():

    result = ExecutionResult(
        success=False,
        transaction_id="tx-2",
        error="failure",
    )

    assert (
        result.success
        is False
    )

    assert (
        result.error
        == "failure"
    )


def test_state_changes():

    result = ExecutionResult(
        success=True,
        transaction_id="tx-3",
        state_changes={
            "alice": 50,
        },
    )

    assert (
        result.state_changes["alice"]
        == 50
    )


def test_snapshot():

    result = ExecutionResult(
        success=True,
        transaction_id="tx-4",
    )

    snapshot = result.snapshot()

    assert (
        "success"
        in snapshot
    )

    assert (
        "transaction_id"
        in snapshot
    )