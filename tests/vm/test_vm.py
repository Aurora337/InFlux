from influx.vm.vm import VirtualMachine
from influx.vm.program import Program
from influx.vm.instruction import Instruction
from influx.vm.opcode import Opcode


def build_program(*instructions):

    program = Program()

    for instruction in instructions:
        program.add_instruction(instruction)

    return program


def test_vm_push():

    program = build_program(
        Instruction(
            Opcode.PUSH,
            [10],
        ),
    )

    vm = VirtualMachine(program)

    vm.step()

    assert vm.stack.peek() == 10

def test_vm_add():

    program = build_program(
        Instruction(
            opcode=Opcode.PUSH,
            operands=[5],
        ),
        Instruction(
            opcode=Opcode.PUSH,
            operands=[7],
        ),
        Instruction(
            opcode=Opcode.ADD,
            operands=[],
        ),
        Instruction(
            opcode=Opcode.HALT,
            operands=[],
        ),
    )

    vm = VirtualMachine(program)

    vm.run()

    assert vm.halted is True
    assert vm.stack.size() == 1
    assert vm.stack.pop() == 12


def test_vm_sub():

    program = build_program(
        Instruction(Opcode.PUSH, [10]),
        Instruction(Opcode.PUSH, [3]),
        Instruction(Opcode.SUB, []),
        Instruction(Opcode.HALT, []),
    )

    vm = VirtualMachine(program)

    vm.run()

    assert vm.stack.pop() == 7


def test_vm_mul():

    program = build_program(
        Instruction(Opcode.PUSH, [4]),
        Instruction(Opcode.PUSH, [5]),
        Instruction(Opcode.MUL, []),
        Instruction(Opcode.HALT, []),
    )

    vm = VirtualMachine(program)

    vm.run()

    assert vm.stack.pop() == 20


def test_vm_div():

    program = build_program(
        Instruction(Opcode.PUSH, [20]),
        Instruction(Opcode.PUSH, [4]),
        Instruction(Opcode.DIV, []),
        Instruction(Opcode.HALT, []),
    )

    vm = VirtualMachine(program)

    vm.run()

    assert vm.stack.pop() == 5


def test_vm_store_and_load():

    program = build_program(
        Instruction(Opcode.PUSH, [99]),
        Instruction(Opcode.STORE, [1]),
        Instruction(Opcode.LOAD, [1]),
        Instruction(Opcode.HALT, []),
    )

    vm = VirtualMachine(program)

    vm.run()

    assert vm.stack.pop() == 99


def test_vm_pop():

    program = build_program(
        Instruction(Opcode.PUSH, [50]),
        Instruction(Opcode.POP, []),
        Instruction(Opcode.HALT, []),
    )

    vm = VirtualMachine(program)

    vm.run()

    assert vm.stack.size() == 0


def test_vm_halt():

    program = build_program(
        Instruction(Opcode.HALT, []),
        Instruction(Opcode.PUSH, [100]),
    )

    vm = VirtualMachine(program)

    result = vm.run()

    assert result.halted is True
    assert vm.stack.size() == 0


def test_vm_reset():

    program = build_program(
        Instruction(Opcode.PUSH, [10]),
        Instruction(Opcode.HALT, []),
    )

    vm = VirtualMachine(program)

    vm.run()

    vm.reset()

    assert vm.program_counter == 0
    assert vm.halted is False
    assert vm.stack.size() == 0


def test_execution_result():

    program = build_program(
        Instruction(Opcode.PUSH, [1]),
        Instruction(Opcode.HALT, []),
    )

    vm = VirtualMachine(program)

    result = vm.run()

    assert result.success
    assert result.halted
    assert result.instructions_executed == 1