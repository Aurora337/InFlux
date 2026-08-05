from influx.vm.instruction import Instruction
from influx.vm.opcode import Opcode
from influx.vm.program import Program


def test_program_creation():

    program = Program()

    assert program.instruction_count() == 0


def test_add_instruction():

    program = Program()

    instruction = Instruction(
        opcode=Opcode.NOP,
        operands=[],
    )

    program.add_instruction(instruction)

    assert program.instruction_count() == 1


def test_get_instruction():

    program = Program()

    instruction = Instruction(
        opcode=Opcode.PUSH,
        operands=[5],
    )

    program.add_instruction(instruction)

    assert program.get(0) is instruction


def test_program_order():

    program = Program()

    first = Instruction(
        Opcode.PUSH,
        [1],
    )

    second = Instruction(
        Opcode.HALT,
        [],
    )

    program.add_instruction(first)
    program.add_instruction(second)

    assert program.get(0) is first
    assert program.get(1) is second