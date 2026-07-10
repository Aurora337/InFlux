from __future__ import annotations

from .transaction import Transaction
from .transaction_policy import TransactionPolicy


class TransactionValidator:
    """
    Validates transactions against deterministic rules.
    """

    def __init__(
        self,
        policy: TransactionPolicy | None = None,
    ) -> None:

        self.policy = (
            policy
            if policy is not None
            else TransactionPolicy()
        )

    def validate_identity(
        self,
        transaction: Transaction,
    ) -> bool:
        """
        Validate transaction identity fields.
        """

        if not transaction.transaction_id:
            return False

        if not transaction.sender:
            return False

        if not transaction.receiver:
            return False

        return True

    def validate_values(
        self,
        transaction: Transaction,
    ) -> bool:
        """
        Validate transaction numeric fields.
        """

        if transaction.amount < 0:
            return False

        if transaction.fee < 0:
            return False

        if transaction.nonce < 0:
            return False

        return True

    def validate_payload(
        self,
        transaction: Transaction,
    ) -> bool:
        """
        Validate payload size.
        """

        payload_size = len(
            str(transaction.payload)
        )

        return (
            payload_size
            <= self.policy.maximum_payload_size
        )

    def validate_fee(
        self,
        transaction: Transaction,
    ) -> bool:
        """
        Validate fee requirements.
        """

        if (
            not self.policy.allow_zero_fee
            and transaction.fee == 0
        ):
            return False

        return (
            transaction.fee
            >= self.policy.minimum_fee
        )

    def validate(
        self,
        transaction: Transaction,
    ) -> bool:
        """
        Complete transaction validation.
        """

        return (
            self.validate_identity(transaction)
            and self.validate_values(transaction)
            and self.validate_payload(transaction)
            and self.validate_fee(transaction)
        )