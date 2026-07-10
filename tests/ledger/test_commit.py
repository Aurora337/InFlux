from influx.ledger.ledger import Ledger
from influx.ledger.commit_engine import (
    CommitEngine,
)


class MockTransaction:

    sender = "alice"

    receiver = "bob"

    amount = 25


class MockBlock:

    transactions = [
        MockTransaction()
    ]



def test_commit_block():

    ledger = Ledger()

    engine = CommitEngine(
        ledger
    )

    result = engine.commit(
        MockBlock()
    )

    assert result is True

    assert (
        ledger.height()
        == 1
    )


def test_transaction_applied():

    ledger = Ledger()

    engine = CommitEngine(
        ledger
    )

    engine.commit(
        MockBlock()
    )

    assert (
        ledger.state.get_account(
            "alice"
        )
        == -25
    )

    assert (
        ledger.state.get_account(
            "bob"
        )
        == 25
    )


def test_snapshot():

    ledger = Ledger()

    engine = CommitEngine(
        ledger
    )

    snapshot = engine.snapshot()

    assert "state" in snapshot
    assert "blocks" in snapshot