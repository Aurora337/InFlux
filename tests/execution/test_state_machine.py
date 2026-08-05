from influx.execution.state_machine import (
    StateMachine,
)


def test_empty_state():

    machine = StateMachine()

    assert (
        machine.snapshot()
        == {}
    )


def test_initial_state():

    machine = StateMachine(
        {
            "alice": 100,
        }
    )

    assert (
        machine.get("alice")
        == 100
    )


def test_set_value():

    machine = StateMachine()

    machine.set(
        "alice",
        50,
    )

    assert (
        machine.get("alice")
        == 50
    )


def test_apply_changes():

    machine = StateMachine()

    machine.apply_changes(
        {
            "alice": 100,
            "bob": 25,
        }
    )

    assert (
        machine.get("alice")
        == 100
    )

    assert (
        machine.get("bob")
        == 25
    )


def test_snapshot():

    machine = StateMachine(
        {
            "node": 10,
        }
    )

    snapshot = machine.snapshot()

    assert (
        snapshot["node"]
        == 10
    )