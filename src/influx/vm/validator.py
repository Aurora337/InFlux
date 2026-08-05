from __future__ import annotations

from .instruction import Instruction
from .opcode import Opcode
from .exceptions import ProgramValidationError


class ProgramValidator:
    """
    Validates VM programs before execution.
    """

    @staticmethod
    def validate_instruction(instruction: Instruction) -> None:

        if not isinstance(instruction.opcode, (Opcode, str)):
            raise ProgramValidationError(
                "invalid opcode type"
            )

        try:
            opcode = (
                instruction.opcode.value
                if isinstance(instruction.opcode, Opcode)
                else instruction.opcode
            )

            Opcode(opcode)
        except ValueError as exc:
            raise ProgramValidationError(
                f"unsupported opcode: {instruction.opcode}"
            ) from exc
    
    @classmethod
    def validate(cls, program) -> None:
        for instruction in program.instructions:
            if not isinstance(instruction, Instruction):
                raise ProgramValidationError(
                    "program contains non-instruction object"
                )

            cls.validate_instruction(instruction)