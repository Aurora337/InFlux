from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class LedgerState:
    """
    Represents canonical network state.
    """

    height: int = 0

    state_root: str = ""

    accounts: dict[str, Any] = field(
        default_factory=dict
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def update_account(
        self,
        account: str,
        value: Any,
    ) -> None:
        """
        Update deterministic account state.
        """

        self.accounts[
            account
        ] = value

    def get_account(
        self,
        account: str,
    ) -> Any | None:
        """
        Retrieve account state.
        """

        return self.accounts.get(
            account
        )

    def snapshot(self) -> dict:
        """
        Deterministic state snapshot.
        """

        return {
            "height":
                self.height,

            "state_root":
                self.state_root,

            "accounts":
                dict(self.accounts),

            "metadata":
                dict(self.metadata),
        }