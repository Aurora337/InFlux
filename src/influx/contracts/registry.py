from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ContractRegistry:
    """
    Deterministic registry of deployed contracts.
    """

    _contracts: dict[str, dict[str, Any]] = field(default_factory=dict)

    def register(
        self,
        contract_id: str,
        metadata: dict[str, Any],
    ) -> None:
        self._contracts[contract_id] = dict(metadata)

    def unregister(
        self,
        contract_id: str,
    ) -> None:
        self._contracts.pop(contract_id, None)

    def exists(
        self,
        contract_id: str,
    ) -> bool:
        return contract_id in self._contracts

    def get(
        self,
        contract_id: str,
    ) -> dict[str, Any]:
        return dict(self._contracts[contract_id])

    def count(self) -> int:
        return len(self._contracts)

    def contract_ids(self) -> list[str]:
        """
        Return deterministic ordering.
        """
        return sorted(self._contracts.keys())