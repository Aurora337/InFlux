from __future__ import annotations

from typing import Any


class RuntimeServices:
    """
    Runtime dependency container.

    Stores initialized runtime services.
    """

    def __init__(self) -> None:
        self._services: dict[str, Any] = {}

    def register(
        self,
        name: str,
        service: Any,
    ) -> None:
        self._services[name] = service

    def get(
        self,
        name: str,
    ) -> Any | None:
        return self._services.get(name)

    def has(
        self,
        name: str,
    ) -> bool:
        return name in self._services

    def names(self) -> list[str]:
        return sorted(self._services.keys())