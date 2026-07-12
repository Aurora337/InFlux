from __future__ import annotations

from enum import Enum


class Opcode(str, Enum):
    """
    Supported deterministic VM opcodes.
    """

    NOP = "NOP"
    PUSH = "PUSH"
    POP = "POP"
    LOAD = "LOAD"
    STORE = "STORE"
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    HALT = "HALT"