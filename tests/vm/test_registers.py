from influx.vm.registers import Registers


def test_register_set_get():

    registers = Registers()

    registers.set("A", 10)

    assert registers.get("A") == 10


def test_register_reset():

    registers = Registers()

    registers.set("A", 7)

    registers.reset()

    assert registers.get("A") == 0


def test_multiple_registers():

    registers = Registers()

    registers.set("A", 1)
    registers.set("B", 2)

    assert registers.get("A") == 1
    assert registers.get("B") == 2