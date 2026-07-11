import pytest

from influx.contracts.gas import GasMeter
from influx.contracts.exceptions import GasExhaustedError


def test_gas_consumption() -> None:
    meter = GasMeter(limit=100)

    meter.consume(25)

    assert meter.consumed == 25
    assert meter.remaining() == 75
    assert meter.exhausted() is False


def test_gas_exhaustion() -> None:
    meter = GasMeter(limit=5)

    with pytest.raises(GasExhaustedError):
        meter.consume(6)


def test_negative_gas() -> None:
    meter = GasMeter(limit=5)

    with pytest.raises(ValueError):
        meter.consume(-1)