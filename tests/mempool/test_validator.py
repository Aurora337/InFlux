from influx.mempool.transaction import Transaction
from influx.mempool.transaction_policy import TransactionPolicy
from influx.mempool.transaction_validator import (
    TransactionValidator,
)


def create_transaction():

    return Transaction(
        transaction_id="tx-1",
        sender="alice",
        receiver="bob",
        amount=100,
        fee=5,
        nonce=1,
        payload={
            "data": "value"
        },
    )


def test_valid_transaction():

    validator = TransactionValidator()

    assert validator.validate(
        create_transaction()
    )


def test_invalid_id():

    validator = TransactionValidator()

    tx = create_transaction()

    tx.transaction_id = ""

    assert not validator.validate(tx)


def test_invalid_sender():

    validator = TransactionValidator()

    tx = create_transaction()

    tx.sender = ""

    assert not validator.validate(tx)


def test_negative_amount():

    validator = TransactionValidator()

    tx = create_transaction()

    tx.amount = -1

    assert not validator.validate(tx)


def test_negative_fee():

    validator = TransactionValidator()

    tx = create_transaction()

    tx.fee = -1

    assert not validator.validate(tx)


def test_zero_fee_disabled():

    policy = TransactionPolicy(
        allow_zero_fee=False,
        minimum_fee=1,
    )

    validator = TransactionValidator(
        policy
    )

    tx = create_transaction()

    tx.fee = 0

    assert not validator.validate(tx)


def test_payload_limit():

    policy = TransactionPolicy(
        maximum_payload_size=5,
    )

    validator = TransactionValidator(
        policy
    )

    tx = create_transaction()

    tx.payload = {
        "very_large": "payload"
    }

    assert not validator.validate(tx)