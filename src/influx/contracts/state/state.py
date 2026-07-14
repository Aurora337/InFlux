from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ContractState:
    """
    Deterministic contract key/value storage.
    """

    _values: dict[str, Any] = field(default_factory=dict)

    def put(
        self,
        key: str,
        value: Any,
    ) -> None:
        self._values[key] = value

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self._values.get(key, default)

    def delete(
        self,
        key: str,
    ) -> None:
        self._values.pop(key, None)

    def contains(
        self,
        key: str,
    ) -> bool:
        return key in self._values

    def clear(self) -> None:
        self._values.clear()

    def size(self) -> int:
        return len(self._values)

    def snapshot(self) -> dict[str, Any]:
        """
        Return a deterministic snapshot.
        """
        return {
            key: self._values[key]
            for key in sorted(self._values)
        }

    def restore(
        self,
        snapshot: dict[str, Any],
    ) -> None:
        self._values = dict(snapshot)

    def to_dict(self) -> dict[str, Any]:
        return self.snapshot()