from __future__ import annotations

from enum import Enum


class BlockState(str, Enum):
    """
    Deterministic block lifecycle.
    """

    CREATED = "created"

    BUILDING = "building"

    SEALED = "sealed"

    VALIDATING = "validating"

    VALID = "valid"

    INVALID = "invalid"

    COMMITTED = "committed"