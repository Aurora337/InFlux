from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .persistence import ContractPersistence
from .registry import ContractRegistry


@dataclass(slots=True)
class ContractDeployment:
    """
    Deterministic contract deployment manager.
    """

    persistence: ContractPersistence
    registry: ContractRegistry

    def deploy(
        self,
        contract_id: str,
        metadata: dict[str, Any],
    ) -> None:
        if self.registry.exists(contract_id):
            raise ValueError(
                f"Contract '{contract_id}' is already deployed."
            )

        self.persistence.save(
            contract_id,
            metadata,
        )

        self.registry.register(
            contract_id,
            metadata,
        )

    def undeploy(
        self,
        contract_id: str,
    ) -> None:
        self.persistence.remove(contract_id)
        self.registry.unregister(contract_id)

    def is_deployed(
        self,
        contract_id: str,
    ) -> bool:
        return self.registry.exists(contract_id)