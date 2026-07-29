"""
Unit tests for Economic Executor (current API).
"""

from influx.economics.economic_executor import (
    EconomicExecutor,
    EconomicOperation,
    OperationType,
)
from influx.economics.economic_state import EconomicState
from influx.economics.economic_context import create_economic_context


class TestEconomicExecutor:
    def _state(self) -> EconomicState:
        state = EconomicState()
        state.get_account("addr_001").balances["INFLUX"] = 1000.0
        state.get_account("addr_002").balances["INFLUX"] = 0.0
        state.supply.total_supply = 1000.0
        state.supply.circulating_supply = 1000.0
        state.update_state_root()
        return state

    def test_execute_transfer(self):
        executor = EconomicExecutor()
        state = self._state()
        ctx = create_economic_context(block_height=1)
        op = EconomicOperation(OperationType.TRANSFER, "addr_001", "addr_002", 100.0)
        receipt = executor.execute(op, state, ctx)
        assert receipt.success is True
        assert state.get_balance("addr_001") == 900.0
        assert state.get_balance("addr_002") == 100.0

    def test_execute_transfer_insufficient(self):
        executor = EconomicExecutor()
        state = self._state()
        ctx = create_economic_context(block_height=1)
        op = EconomicOperation(OperationType.TRANSFER, "addr_001", "addr_002", 9999.0)
        receipt = executor.execute(op, state, ctx)
        assert receipt.success is False

    def test_execute_mint(self):
        executor = EconomicExecutor()
        state = self._state()
        ctx = create_economic_context(block_height=1)
        op = EconomicOperation(OperationType.MINT, "", "addr_001", 500.0)
        receipt = executor.execute(op, state, ctx)
        assert receipt.success is True
        assert state.get_balance("addr_001") == 1500.0
        assert state.supply.total_supply == 1500.0

    def test_execute_burn(self):
        executor = EconomicExecutor()
        state = self._state()
        ctx = create_economic_context(block_height=1)
        op = EconomicOperation(OperationType.BURN, "addr_001", "", 300.0)
        receipt = executor.execute(op, state, ctx)
        assert receipt.success is True
        assert state.get_balance("addr_001") == 700.0
        assert state.supply.total_supply == 700.0

    def test_execute_lock_unlock(self):
        executor = EconomicExecutor()
        state = self._state()
        ctx = create_economic_context(block_height=1)

        lock = EconomicOperation(OperationType.LOCK, "addr_001", "", 200.0)
        unlock = EconomicOperation(OperationType.UNLOCK, "addr_001", "", 100.0)

        r1 = executor.execute(lock, state, ctx)
        r2 = executor.execute(unlock, state, ctx)

        assert r1.success is True
        assert r2.success is True
        assert state.get_account("addr_001").locked_balances.get("INFLUX", 0.0) == 100.0

    def test_snapshot_and_reset(self):
        executor = EconomicExecutor()
        snap = executor.snapshot()
        assert "execution_count" in snap
        assert "chain_valid" in snap
        assert "transitions" in snap

        state = self._state()
        ctx = create_economic_context(block_height=1)
        op = EconomicOperation(OperationType.TRANSFER, "addr_001", "addr_002", 100.0)
        executor.execute(op, state, ctx)
        assert executor.get_execution_count() == 1

        executor.reset()
        assert executor.get_execution_count() == 0
