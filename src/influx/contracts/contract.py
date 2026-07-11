from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Contract:
    """
    Deterministic smart contract definition.
    """

    contract_id: str
    owner: str
    version: str
    code_hash: str

    def identity(self) -> str:
        """
        Return the deterministic contract identifier.
        """
        return self.contract_id