from influx.contracts.events import (
    ContractEvent,
    EventEmitter,
)


def test_emit_event() -> None:
    emitter = EventEmitter()

    event = ContractEvent(
        event_name="Transfer",
        contract_id="contract-1",
        payload={
            "from": "alice",
            "to": "bob",
            "amount": 100,
        },
    )

    emitter.emit(event)

    assert emitter.count() == 1
    assert emitter.all_events()[0] == event