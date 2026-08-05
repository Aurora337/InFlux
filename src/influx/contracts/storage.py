from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ContractStorage:
    """
    Deterministic key/value storage for a contract.
    """

    _values: dict[str, str] = field(default_factory=dict)

    def put(
        self,
        key: str,
        value: str,
    ) -> None:
        """
        Store a value.
        """

        self._values[str(key)] = str(value)

    def get(
        self,
        key: str,
        default: str | None = None,
    ) -> str | None:
        """
        Retrieve a value.
        """

        return self._values.get(str(key), default)

    def contains(
        self,
        key: str,
    ) -> bool:
        """
        Check if a key exists.
        """

        return str(key) in self._values

    def remove(
        self,
        key: str,
    ) -> None:
        """
        Remove a key if present.
        """

        self._values.pop(str(key), None)

    def snapshot(self) -> dict[str, str]:
        """
        Deterministic storage snapshot.
        """

        return dict(sorted(self._values.items()))