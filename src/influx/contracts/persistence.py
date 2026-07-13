from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ContractPersistence:
    """
    Deterministic persistence layer for deployed contracts.
    """

    _contracts: dict[str, dict[str, Any]] = field(default_factory=dict)

    def save(
        self,
        contract_id: str,
        metadata: dict[str, Any],
    ) -> None:
        """
        Persist contract metadata.
        """
        self._contracts[contract_id] = dict(metadata)

    def load(
        self,
        contract_id: str,
    ) -> dict[str, Any]:
        """
        Load persisted metadata.
        """
        return dict(self._contracts[contract_id])

    def exists(
        self,
        contract_id: str,
    ) -> bool:
        """
        Determine whether a contract is persisted.
        """
        return contract_id in self._contracts

    def remove(
        self,
        contract_id: str,
    ) -> None:
        """
        Remove persisted contract metadata.
        """
        self._contracts.pop(contract_id, None)

    def count(self) -> int:
        """
        Return number of persisted contracts.
        """
        return len(self._contracts)

    def snapshot(self) -> dict[str, dict[str, Any]]:
        """
        Deterministic persistence snapshot.
        """
        return {
            key: dict(self._contracts[key])
            for key in sorted(self._contracts)
        }