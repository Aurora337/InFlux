from influx.ledger.ledger_state import (
    LedgerState,
)

from influx.ledger.state_transition import (
    StateTransition,
)


class MockTransaction:

    sender = "alice"

    receiver = "bob"

    amount = 50



def test_apply_transaction():

    state = LedgerState()

    transition = StateTransition()

    transition.apply(
        state,
        MockTransaction(),
    )

    assert (
        state.get_account("alice")
        == -50
    )

    assert (
        state.get_account("bob")
        == 50
    )


def test_existing_balances():

    state = LedgerState()

    state.update_account(
        "alice",
        100,
    )

    state.update_account(
        "bob",
        25,
    )

    transition = StateTransition()

    transition.apply(
        state,
        MockTransaction(),
    )

    assert (
        state.get_account("alice")
        == 50
    )

    assert (
        state.get_account("bob")
        == 75
    )


def test_account_lookup():

    state = LedgerState()

    state.update_account(
        "node",
        10,
    )

    assert (
        state.get_account("node")
        == 10
    )


def test_missing_account():

    state = LedgerState()

    assert (
        state.get_account("missing")
        is None
    )


def test_state_snapshot():

    state = LedgerState()

    snapshot = state.snapshot()

    assert "height" in snapshot
    assert "accounts" in snapshot