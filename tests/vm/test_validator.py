import pytest

from influx.vm.exceptions import ProgramValidationError
from influx.vm.instruction import Instruction
from influx.vm.opcode import Opcode
from influx.vm.program import Program
from influx.vm.validator import ProgramValidator


def test_valid_program():

    program = Program()

    program.add_instruction(
        Instruction(
            opcode=Opcode.PUSH,
            operands=[1],
        )
    )

    ProgramValidator.validate(program)


def test_invalid_opcode():

    program = Program()

    program.add_instruction(
        Instruction(
            opcode="INVALID",
            operands=[],
        )
    )

    with pytest.raises(ProgramValidationError):
        ProgramValidator.validate(program)


def test_invalid_instruction_object():

    program = Program()

    program.instructions.append(object())

    with pytest.raises(ProgramValidationError):
        ProgramValidator.validate(program)