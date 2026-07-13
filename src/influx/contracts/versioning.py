from __future__ import annotations

from dataclasses import dataclass, field

from .snapshot import ContractSnapshot
from .state import ContractState


@dataclass(slots=True)
class ContractVersionManager:
    """
    Deterministic contract state version manager.
    """

    _versions: dict[int, ContractSnapshot] = field(
        default_factory=dict,
    )

    def create_version(
        self,
        version: int,
        state: ContractState,
    ) -> None:
        if version in self._versions:
            raise ValueError(
                f"Version {version} already exists."
            )

        self._versions[version] = ContractSnapshot.create(
            state,
        )

    def restore_version(
        self,
        version: int,
        state: ContractState,
    ) -> None:
        if version not in self._versions:
            raise ValueError(
                f"Unknown version: {version}"
            )

        self._versions[version].restore(
            state,
        )

    def exists(
        self,
        version: int,
    ) -> bool:
        return version in self._versions

    def versions(self) -> list[int]:
        return sorted(self._versions.keys())

    def count(self) -> int:
        return len(self._versions)