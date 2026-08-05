from __future__ import annotations

from enum import Enum


class TransactionState(str, Enum):
    """
    Deterministic transaction lifecycle.
    """

    CREATED = "created"

    PENDING = "pending"

    VALIDATING = "validating"

    VALID = "valid"

    INVALID = "invalid"

    SCHEDULED = "scheduled"

    EXECUTED = "executed"

    DROPPED = "dropped"