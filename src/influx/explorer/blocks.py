from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class BlockRecord:
    """
    Explorer block representation.
    """

    height: int

    block_hash: str

    previous_hash: str

    timestamp: int

    transaction_ids: list[str] = field(
        default_factory=list,
    )