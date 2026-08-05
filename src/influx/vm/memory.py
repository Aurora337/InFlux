from __future__ import annotations


class Memory:
    """
    Deterministic VM memory.
    """

    def __init__(self) -> None:
        self._storage: dict[int, object] = {}

    def load(self, address: int) -> int | float:
        value = self._storage.get(address, 0)

        if isinstance(value, (int, float)):
            return value
        
        raise TypeError("memory value must be numeric")

    def store(
        self,
        address: int,
        value: int | float,
    ) -> None:
        
        self._storage[address] = value

    def clear(self) -> None:
        self._storage.clear()