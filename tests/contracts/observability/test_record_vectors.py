from influx.contracts.observability.record import (
    ContractExecutionRecord,
)


def create_record(
    sequence=2,
):
    return ContractExecutionRecord(
        record_id="record_001",
        trace_id="trace_001",
        executor="node_001",
        sequence=sequence,
    )


def test_record_creation():

    record = create_record()

    assert record.record_id == "record_001"


def test_record_serialization():

    record = create_record()

    exported = record.to_dict()

    assert exported["trace_id"] == "trace_001"


def test_record_executor():

    record = create_record()

    assert record.executor == "node_001"


def test_record_sequence():

    record = create_record()

    assert record.sequence == 2


def test_record_ordering():

    previous = create_record(1)
    current = create_record(2)

    assert current.follows(previous)


def test_record_determinism():

    first = create_record()
    second = create_record()

    assert first.to_dict() == second.to_dict()