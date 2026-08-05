from influx.vm.opcode import Opcode


def test_opcode_values():

    assert Opcode.NOP.value == "NOP"
    assert Opcode.PUSH.value == "PUSH"
    assert Opcode.POP.value == "POP"
    assert Opcode.LOAD.value == "LOAD"
    assert Opcode.STORE.value == "STORE"
    assert Opcode.ADD.value == "ADD"
    assert Opcode.SUB.value == "SUB"
    assert Opcode.MUL.value == "MUL"
    assert Opcode.DIV.value == "DIV"
    assert Opcode.HALT.value == "HALT"


def test_opcode_lookup():

    assert Opcode("ADD") is Opcode.ADD
    assert Opcode("HALT") is Opcode.HALT


def test_opcode_count():

    assert len(Opcode) >= 10