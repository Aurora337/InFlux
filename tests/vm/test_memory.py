from influx.vm.memory import Memory


def test_memory_store_load():

    memory = Memory()

    memory.store(0, 100)

    assert memory.load(0) == 100


def test_memory_default():

    memory = Memory()

    assert memory.load(999) == 0


def test_memory_overwrite():

    memory = Memory()

    memory.store(1, 10)
    memory.store(1, 20)

    assert memory.load(1) == 20


def test_memory_clear():

    memory = Memory()

    memory.store(2, 50)

    memory.clear()

    assert memory.load(2) == 0