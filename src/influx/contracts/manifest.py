from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ContractManifest:
    """
    Deterministic contract identity manifest.
    """

    contract_id: str
    owner: str
    version: str
    code_hash: str

    def to_dict(self) -> dict[str, Any]:
        """
        Export deterministic manifest data.
        """
        return {
            "contract_id": self.contract_id,
            "owner": self.owner,
            "version": self.version,
            "code_hash": self.code_hash,
        }

    def identity(self) -> str:
        """
        Return deterministic contract identity string.
        """
        return (
            f"{self.contract_id}:"
            f"{self.version}:"
            f"{self.code_hash}"
        )