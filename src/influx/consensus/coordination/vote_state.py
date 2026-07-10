from __future__ import annotations

from enum import Enum


class VoteState(str, Enum):
    """
    Deterministic voting lifecycle.
    """

    CREATED = "created"

    CAST = "cast"

    VERIFIED = "verified"

    ACCEPTED = "accepted"

    REJECTED = "rejected"