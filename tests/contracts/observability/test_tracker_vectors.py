from influx.contracts.observability.tracker import (
    ContractExecutionTracker,
)
from influx.contracts.observability.trace import (
    ContractExecutionTrace,
)
from influx.contracts.observability.record import (
    ContractExecutionRecord,
)


def create_trace():
    return ContractExecutionTrace(
        trace_id="trace_001",
        contract_id="contract_001",
        operation="execute",
        status="completed",
    )


def create_record():
    return ContractExecutionRecord(
        record_id="record_001",
        trace_id="trace_001",
        executor="node_001",
        sequence=1,
    )


def test_add_trace():

    tracker = ContractExecutionTracker()

    tracker.add_trace(create_trace())

    assert tracker.trace_count() == 1


def test_record_execution():

    tracker = ContractExecutionTracker()

    tracker.record(create_record())

    assert tracker.record_count() == 1


def test_multiple_records():

    tracker = ContractExecutionTracker()

    tracker.record(create_record())
    tracker.record(create_record())

    assert tracker.record_count() == 2


def test_multiple_traces():

    tracker = ContractExecutionTracker()

    tracker.add_trace(create_trace())
    tracker.add_trace(create_trace())

    assert tracker.trace_count() == 2


def test_tracker_is_deterministic():

    tracker = ContractExecutionTracker()

    tracker.add_trace(create_trace())
    tracker.record(create_record())

    assert tracker.trace_count() == 1
    assert tracker.record_count() == 1


def test_tracker_defaults():

    tracker = ContractExecutionTracker()

    assert tracker.trace_count() == 0
    assert tracker.record_count() == 0