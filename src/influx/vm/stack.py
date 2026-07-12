from __future__ import annotations


class Stack:
    """
    Deterministic VM stack.
    """

    def __init__(self) -> None:
        self._items: list[int | float] = []

    def push(self, value: int | float,) -> None:
        self._items.append(value)

    def pop(self) -> int | float:
        if not self._items:
            raise IndexError("stack underflow")

        return self._items.pop()

    def peek(self) -> int | float:
        if not self._items:
            raise IndexError("stack empty")

        return self._items[-1]

    def clear(self) -> None:
        self._items.clear()

    def size(self) -> int:
        return len(self._items)