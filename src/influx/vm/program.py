from __future__ import annotations

from dataclasses import dataclass, field

from .instruction import Instruction


@dataclass(slots=True)
class Program:
    """
    Deterministic VM program.
    """

    instructions: list[Instruction] = field(default_factory=list)

    def add_instruction(
        self,
        instruction: Instruction,
    ) -> None:
        self.instructions.append(instruction)

    def instruction_count(self) -> int:
        return len(self.instructions)

    def get(
        self,
        index: int,
    ) -> Instruction:
        return self.instructions[index]