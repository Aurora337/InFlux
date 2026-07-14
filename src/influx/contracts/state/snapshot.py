from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class StateSnapshot:
    """
    Immutable deterministic contract state snapshot.
    """

    contract_id: str
    version: str
    state: dict[str, Any]
    height: int

    def to_dict(self) -> dict[str, Any]:
        """
        Return deterministic snapshot representation.
        """
        return {
            "contract_id": self.contract_id,
            "version": self.version,
            "state": self.state,
            "height": self.height,
        }

    def keys(self) -> list[str]:
        """
        Return sorted state keys.
        """
        return sorted(self.state.keys())

    def same_state(
        self,
        other: "StateSnapshot",
    ) -> bool:
        """
        Compare state contents deterministically.
        """
        return (
            self.contract_id == other.contract_id
            and self.version == other.version
            and self.state == other.state
            and self.height == other.height
        )