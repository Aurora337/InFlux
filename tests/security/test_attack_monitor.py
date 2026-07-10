from influx.security.attack_monitor import (
    AttackEvent,
    AttackMonitor,
)


def test_record_attack():

    monitor = AttackMonitor()

    event = AttackEvent(
        source="node-1",
        attack_type="spam",
        severity=5,
    )

    monitor.record(
        event
    )

    assert (
        monitor.count()
        == 1
    )


def test_attack_event_storage():

    monitor = AttackMonitor()

    event = AttackEvent(
        source="node-1",
        attack_type="conflict",
        severity=8,
    )

    monitor.record(
        event
    )

    events = monitor.events()

    assert len(events) == 1

    assert (
        events[0].attack_type
        == "conflict"
    )


def test_empty_monitor():

    monitor = AttackMonitor()

    assert (
        monitor.count()
        == 0
    )

    assert (
        monitor.events()
        == []
    )