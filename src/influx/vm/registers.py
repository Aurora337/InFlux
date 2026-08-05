from __future__ import annotations


class Registers:
    """
    Deterministic VM registers.
    """

    def __init__(self) -> None:
        self._registers: dict[str, object] = {}

    def set(
        self,
        name: str,
        value: object,
    ) -> None:
        self._registers[name] = value

    def get(
        self,
        name: str,
    ) -> object:
        return self._registers.get(name, 0)

    def reset(self) -> None:
        self._registers.clear()