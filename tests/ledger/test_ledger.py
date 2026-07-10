from influx.ledger.ledger import Ledger
from influx.ledger.ledger_state import LedgerState


def test_default_state():

    ledger = Ledger()

    assert (
        ledger.state.height
        == 0
    )

    assert (
        len(ledger.blocks)
        == 0
    )


def test_custom_state():

    state = LedgerState(
        height=5,
        state_root="root",
    )

    ledger = Ledger(
        state
    )

    assert (
        ledger.height()
        == 5
    )


def test_append_block():

    ledger = Ledger()

    block = object()

    ledger.append_block(
        block
    )

    assert (
        len(ledger.blocks)
        == 1
    )

    assert (
        ledger.height()
        == 1
    )


def test_latest_block():

    ledger = Ledger()

    block = object()

    ledger.append_block(
        block
    )

    assert (
        ledger.latest_block()
        is block
    )


def test_latest_block_empty():

    ledger = Ledger()

    assert (
        ledger.latest_block()
        is None
    )


def test_snapshot():

    ledger = Ledger()

    snapshot = ledger.snapshot()

    assert "state" in snapshot
    assert "blocks" in snapshot