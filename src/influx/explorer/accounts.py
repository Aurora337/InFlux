from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class AccountRecord:
    """
    Explorer account representation.
    """

    address: str

    balance: int = 0

    transaction_count: int = 0

    transaction_ids: list[str] = field(
        default_factory=list,
    )