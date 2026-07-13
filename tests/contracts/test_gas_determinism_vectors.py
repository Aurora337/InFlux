import pytest

from influx.contracts.gas import GasMeter


def create_gas_meter():
    return GasMeter(limit=100)


def test_initial_gas_state_is_deterministic():
    gas_a = create_gas_meter()
    gas_b = create_gas_meter()

    assert gas_a.remaining() == gas_b.remaining()
    assert gas_a.remaining() == 100


def test_same_consumption_produces_same_remaining_gas():
    gas_a = create_gas_meter()
    gas_b = create_gas_meter()

    gas_a.consume(25)
    gas_b.consume(25)

    assert gas_a.remaining() == gas_b.remaining()
    assert gas_a.remaining() == 75


def test_gas_exhaustion_is_deterministic():
    gas = create_gas_meter()

    gas.consume(100)

    assert gas.remaining() == 0

    with pytest.raises(Exception):
        gas.consume(1)


def test_gas_isolation_between_executions():
    gas_a = create_gas_meter()
    gas_b = create_gas_meter()

    gas_a.consume(40)

    assert gas_a.remaining() == 60
    assert gas_b.remaining() == 100


def test_gas_accounting_stability():
    gas_a = create_gas_meter()
    gas_b = create_gas_meter()

    operations = [10, 20, 15]

    for amount in operations:
        gas_a.consume(amount)
        gas_b.consume(amount)

    assert gas_a.remaining() == gas_b.remaining()
    assert gas_a.remaining() == 55