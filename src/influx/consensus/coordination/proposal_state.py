from __future__ import annotations

from enum import Enum


class ProposalState(str, Enum):
    """
    Deterministic proposal lifecycle.
    """

    CREATED = "created"

    SUBMITTED = "submitted"

    VALIDATING = "validating"

    ACCEPTED = "accepted"

    REJECTED = "rejected"

    FINALIZED = "finalized"

    EXPIRED = "expired"