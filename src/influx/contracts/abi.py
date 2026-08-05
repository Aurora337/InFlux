from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ContractFunction:
    """
    Deterministic contract function definition.
    """

    name: str
    parameters: tuple[str, ...]
    return_type: str


@dataclass(slots=True)
class ContractABI:
    """
    Contract application binary interface.
    """

    functions: dict[str, ContractFunction]

    def __init__(self) -> None:
        self.functions = {}

    def register(
        self,
        function: ContractFunction,
    ) -> None:
        """
        Register contract function.
        """

        self.functions[function.name] = function

    def get(
        self,
        name: str,
    ) -> ContractFunction:
        return self.functions[name]

    def count(self) -> int:
        return len(self.functions)