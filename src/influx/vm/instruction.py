from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Instruction:
    """
    Deterministic VM instruction.
    """

    opcode: str
    operands: tuple[str, ...] = ()

    def operand_count(self) -> int:
        return len(self.operands)