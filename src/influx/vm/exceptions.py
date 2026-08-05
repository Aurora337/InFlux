from __future__ import annotations


class VMError(Exception):
    """Base exception for the InFlux Virtual Machine."""


class InvalidInstructionError(VMError):
    """Raised when an instruction is invalid."""


class StackUnderflowError(VMError):
    """Raised when the VM stack underflows."""


class MemoryAccessError(VMError):
    """Raised when invalid memory is accessed."""


class ProgramValidationError(VMError):
    """Raised when a program fails validation."""