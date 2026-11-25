from influx.contracts.observability.history import (
    ContractExecutionHistory,
)
from influx.contracts.observability.record import (
    ContractExecutionRecord,
)


def create_record(
    record_id="record_001",
    sequence=1,
):
    return ContractExecutionRecord(
        record_id=record_id,
        trace_id="trace_001",
        executor="node_001",
        sequence=sequence,
    )


def test_history_add():

    history = ContractExecutionHistory()

    history.add(create_record())

    assert history.count() == 1


def test_history_lookup():

    history = ContractExecutionHistory()

    history.add(create_record())

    assert history.get("record_001") is not None


def test_missing_record():

    history = ContractExecutionHistory()

    assert history.get("missing") is None


def test_history_ordering():

    history = ContractExecutionHistory()

    history.add(create_record("b", 2))
    history.add(create_record("a", 1))

    ordered = history.ordered()

    assert ordered[0].record_id == "a"


def test_history_clear():

    history = ContractExecutionHistory()

    history.add(create_record())

    history.clear()

    assert history.count() == 0


def test_history_deterministic():

    history = ContractExecutionHistory()

    history.add(create_record())

    first = history.ordered()
    second = history.ordered()

    assert first == second