from influx.contracts.observability.trace import (
    ContractExecutionTrace,
)


def create_trace():
    return ContractExecutionTrace(
        trace_id="trace_001",
        contract_id="contract_001",
        operation="execute",
        status="completed",
    )


def test_trace_creation():

    trace = create_trace()

    assert trace.trace_id == "trace_001"


def test_trace_serialization():

    trace = create_trace()

    exported = trace.to_dict()

    assert exported["contract_id"] == "contract_001"


def test_trace_operation():

    trace = create_trace()

    assert trace.operation == "execute"


def test_trace_completion():

    trace = create_trace()

    assert trace.is_complete()


def test_trace_determinism():

    first = create_trace()
    second = create_trace()

    assert first.to_dict() == second.to_dict()


def test_trace_immutability():

    trace = create_trace()

    try:
        trace.status = "failed"
    except Exception:
        assert True
    else:
        assert False