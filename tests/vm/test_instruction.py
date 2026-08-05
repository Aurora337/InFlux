from influx.vm.instruction import Instruction
from influx.vm.opcode import Opcode


def test_instruction_creation():

    instruction = Instruction(
        opcode=Opcode.PUSH,
        operands=[10],
    )

    assert instruction.opcode == Opcode.PUSH
    assert instruction.operands == [10]


def test_instruction_without_operands():

    instruction = Instruction(
        opcode=Opcode.HALT,
        operands=[],
    )

    assert instruction.operands == []


def test_instruction_is_dataclass():

    instruction = Instruction(
        opcode=Opcode.NOP,
        operands=[],
    )

    assert hasattr(instruction, "opcode")
    assert hasattr(instruction, "operands")