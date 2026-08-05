"""
Unit tests for Economic Engine orchestration (current API).
"""

from influx.economics.economic_engine import EconomicEngine, BlockResult
from influx.economics.economic_executor import EconomicOperation, OperationType


class TestEconomicEngine:
    def _seed_balances(self, engine: EconomicEngine) -> None:
        state = engine.get_state()
        state.get_account("addr_001").balances["INFLUX"] = 1000.0
        state.get_account("addr_002").balances["INFLUX"] = 0.0
        state.supply.total_supply = 1000.0
        state.supply.circulating_supply = 1000.0
        state.update_state_root()

    def test_initial_state(self):
        engine = EconomicEngine()
        state = engine.get_state()
        assert state.current_epoch == 0
        assert state.supply.total_supply == 0.0
        assert engine.get_context().block_height == 0

    def test_process_block_empty(self):
        engine = EconomicEngine()
        result = engine.process_block(block_height=1)
        assert isinstance(result, BlockResult)
        assert result.block_height == 1
        assert result.operation_count == 0
        assert result.success_count == 0
        assert result.failure_count == 0

    def test_process_block_with_operations(self):
        engine = EconomicEngine()
        self._seed_balances(engine)
        state = engine.get_state()

        ops = [
            EconomicOperation(
                operation_type=OperationType.TRANSFER,
                from_account="addr_001",
                to_account="addr_002",
                amount=100.0,
            ),
            EconomicOperation(
                operation_type=OperationType.MINT,
                from_account="",
                to_account="addr_001",
                amount=500.0,
            ),
        ]
        result = engine.process_block(block_height=1, operations=ops)
        assert result.operation_count == 2
        assert result.success_count == 2
        assert result.failure_count == 0
        assert state.get_balance("addr_001") == 1400.0
        assert state.get_balance("addr_002") == 100.0
        assert state.supply.total_supply == 1500.0

    def test_process_block_with_failures(self):
        engine = EconomicEngine()
        self._seed_balances(engine)
        state = engine.get_state()

        ops = [
            EconomicOperation(
                operation_type=OperationType.TRANSFER,
                from_account="addr_001",
                to_account="addr_002",
                amount=9999.0,
            ),
            EconomicOperation(
                operation_type=OperationType.BURN,
                from_account="addr_001",
                to_account="",
                amount=50.0,
            ),
        ]
        result = engine.process_block(block_height=1, operations=ops)
        assert result.operation_count == 2
        assert result.success_count == 1
        assert result.failure_count == 1
        assert state.get_balance("addr_001") == 950.0

    def test_execute_operation_direct(self):
        engine = EconomicEngine()
        self._seed_balances(engine)
        state = engine.get_state()

        op = EconomicOperation(
            operation_type=OperationType.BURN,
            from_account="addr_001",
            to_account="",
            amount=200.0,
        )
        receipt = engine.execute_operation(op)
        assert receipt.success is True
        assert state.get_balance("addr_001") == 800.0
        assert state.supply.total_supply == 800.0

    def test_schedule_operation(self):
        engine = EconomicEngine()
        op = EconomicOperation(
            operation_type=OperationType.MINT,
            from_account="",
            to_account="addr_001",
            amount=1000.0,
        )
        assert engine.schedule_operation(operation=op, target_block_height=100, description="Scheduled mint")

    def test_snapshot(self):
        engine = EconomicEngine()
        self._seed_balances(engine)
        snap = engine.snapshot()
        assert "engine_id" in snap
        assert "state" in snap
        assert "context" in snap
        assert "executor" in snap
        assert "scheduler" in snap
        assert "metrics" in snap
        assert "invariants" in snap

    def test_reset(self):
        engine = EconomicEngine()
        self._seed_balances(engine)
        state = engine.get_state()
        assert state.supply.total_supply == 1000.0
        engine.reset()
        assert engine.get_state().supply.total_supply == 0.0
        assert engine.get_context().block_height == 0
