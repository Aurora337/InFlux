"""
Unit tests for Economic Validator (current API).
"""

from influx.economics.economic_validator import EconomicValidator, ValidationResult
from influx.economics.economic_state import EconomicState
from influx.economics.economic_context import create_economic_context
from influx.economics.economic_executor import EconomicOperation, OperationType


class TestValidationResult:
    def test_valid_result(self):
        result = ValidationResult(valid=True)
        assert result.valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_invalid_result(self):
        result = ValidationResult(valid=False, errors=["x"])
        assert result.valid is False
        assert len(result.errors) == 1


class TestEconomicValidator:
    def _state(self):
        state = EconomicState()
        state.get_account("addr_001").balances["INFLUX"] = 1000.0
        state.get_account("addr_001").locked_balances["INFLUX"] = 200.0
        state.get_account("addr_002").balances["INFLUX"] = 0.0
        state.supply.total_supply = 1000.0
        state.supply.circulating_supply = 1000.0
        state.supply.locked_supply = 200.0
        state.update_state_root()
        return state

    def test_validate_valid_operations(self):
        v = EconomicValidator()
        s = self._state()
        c = create_economic_context(block_height=1)

        ops = [
            EconomicOperation(OperationType.TRANSFER, "addr_001", "addr_002", 100.0),
            EconomicOperation(OperationType.MINT, "", "addr_001", 10.0),
            EconomicOperation(OperationType.BURN, "addr_001", "", 10.0),
            EconomicOperation(OperationType.LOCK, "addr_001", "", 10.0),
            EconomicOperation(OperationType.UNLOCK, "addr_001", "", 10.0),
        ]
        for op in ops:
            r = v.validate(op, s, c)
            assert r.valid is True

    def test_invalid_balances_and_malformed(self):
        v = EconomicValidator()
        s = self._state()
        c = create_economic_context(block_height=1)

        insufficient = EconomicOperation(OperationType.TRANSFER, "addr_001", "addr_002", 99999.0)
        malformed = EconomicOperation(OperationType.TRANSFER, "", "addr_002", 1.0)
        negative = EconomicOperation(OperationType.MINT, "", "addr_001", -1.0)

        assert v.validate(insufficient, s, c).valid is False
        assert v.validate(malformed, s, c).valid is False
        assert v.validate(negative, s, c).valid is False

    def test_validator_does_not_mutate_state(self):
        v = EconomicValidator()
        s = self._state()
        before = s.snapshot()
        c = create_economic_context(block_height=1)
        op = EconomicOperation(OperationType.TRANSFER, "addr_001", "addr_002", 100.0)
        _ = v.validate(op, s, c)
        after = s.snapshot()
        assert before == after

    def test_deterministic_validation_result(self):
        v = EconomicValidator()
        s = self._state()
        c = create_economic_context(block_height=1)
        op = EconomicOperation(OperationType.TRANSFER, "addr_001", "addr_002", 100.0)
        r1 = v.validate(op, s, c)
        r2 = v.validate(op, s, c)
        assert r1.valid == r2.valid
        assert r1.errors == r2.errors
