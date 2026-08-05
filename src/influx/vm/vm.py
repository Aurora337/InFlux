from __future__ import annotations

from dataclasses import dataclass, field

from .instruction import Instruction
from .memory import Memory
from .program import Program
from .registers import Registers
from .stack import Stack
from .validator import ProgramValidator
from .opcode import Opcode


@dataclass(slots=True)
class ExecutionResult:
    """
    Result of deterministic VM execution.
    """

    success: bool
    instructions_executed: int
    halted: bool


@dataclass(slots=True)
class VirtualMachine:
    """
    Deterministic InFlux Virtual Machine.
    """

    program: Program

    stack: Stack = field(default_factory=Stack)
    memory: Memory = field(default_factory=Memory)
    registers: Registers = field(default_factory=Registers)

    program_counter: int = 0
    halted: bool = False

    def reset(self) -> None:
        self.program_counter = 0
        self.halted = False
        self.stack.clear()
        self.memory.clear()
        self.registers.reset()

    def load_program(self, program: Program) -> None:
        ProgramValidator.validate(program)
        self.program = program
        self.reset()

    def step(self) -> None:
        if self.program_counter >= self.program.instruction_count():
            self.halted = True
            return

        instruction: Instruction = self.program.get(self.program_counter)

        opcode = (
            instruction.opcode.value
            if isinstance(instruction.opcode, Opcode)
            else str(instruction.opcode)
        )

        if opcode == "NOP":
            pass

        elif opcode == "PUSH":
            
            value = instruction.operands[0]

            if not isinstance(value, (int, float)):
                raise TypeError("PUSH requires numeric operand")
            
            self.stack.push(value)

        elif opcode == "POP":
            self.stack.pop()

        elif opcode == "LOAD":
            address = int(instruction.operands[0])
            self.stack.push(self.memory.load(address))

        elif opcode == "STORE":
            address = int(instruction.operands[0])
            self.memory.store(address, self.stack.pop())

        elif opcode == "ADD":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.push(a + b)

        elif opcode == "SUB":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.push(a - b)

        elif opcode == "MUL":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.push(a * b)

        elif opcode == "DIV":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.push(a / b)

        elif opcode == "HALT":
            self.halted = True
            return

        self.program_counter += 1

    def run(self) -> ExecutionResult:
        ProgramValidator.validate(self.program)

        while not self.halted:
            self.step()

        return ExecutionResult(
            success=True,
            instructions_executed=self.program_counter,
            halted=self.halted,
        )