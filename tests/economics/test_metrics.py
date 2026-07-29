"""
Unit tests for Economic Metrics (current API).
"""

from influx.economics.economic_metrics import EconomicMetrics
from influx.economics.economic_state import EconomicState
from influx.economics.economic_executor import (
    ExecutionReceipt,
    EconomicOperation,
    OperationType,
)


class TestEconomicMetrics:
    def _state(self):
        s = EconomicState()
        s.get_account("addr_001").balances["INFLUX"] = 1000.0
        s.supply.total_supply = 1000.0
        s.supply.circulating_supply = 900.0
        s.supply.locked_supply = 100.0
        s.reserve.reserve_size = 500.0
        s.reserve.current_ratio = 0.5
        s.current_epoch = 5
        s.update_state_root()
        return s

    def _receipt(self, success=True, op_type=OperationType.TRANSFER):
        op = EconomicOperation(op_type, "addr_001", "addr_002", 100.0)
        return ExecutionReceipt(
            operation=op,
            transition=None,
            pre_state_root="abc",
            post_state_root="def" if success else "abc",
            success=success,
            error="" if success else "failed",
        )

    def test_initial_metrics(self):
        metrics = EconomicMetrics()
        assert metrics.total_operations == 0
        assert metrics.successful_operations == 0
        assert metrics.failed_operations == 0
        assert metrics.total_blocks_tracked == 0

    def test_record_execution_success_and_failure(self):
        metrics = EconomicMetrics()
        metrics.record_execution(self._receipt(success=True))
        metrics.record_execution(self._receipt(success=False))

        assert metrics.total_operations == 2
        assert metrics.successful_operations == 1
        assert metrics.failed_operations == 1
        assert metrics.get_success_rate() == 0.5

    def test_record_block_observer_only(self):
        metrics = EconomicMetrics()
        state = self._state()
        before = state.snapshot()

        metrics.record_block(state)

        after = state.snapshot()
        assert before == after  # metrics do not mutate state
        assert metrics.total_blocks_tracked == 1
        assert metrics.last_total_supply == 1000.0
        assert metrics.last_reserve_size == 500.0

    def test_operation_counts_and_snapshot(self):
        metrics = EconomicMetrics()
        metrics.record_execution(self._receipt(success=True, op_type=OperationType.TRANSFER))
        metrics.record_execution(self._receipt(success=True, op_type=OperationType.MINT))

        assert metrics.get_operation_count_by_type(OperationType.TRANSFER) == 1
        assert metrics.get_operation_count_by_type(OperationType.MINT) == 1

        snap = metrics.snapshot()
        assert snap["total_operations"] == 2
        assert snap["successful_operations"] == 2
        assert "operations_by_type" in snap

    def test_reset(self):
        metrics = EconomicMetrics()
        metrics.record_execution(self._receipt(success=True))
        assert metrics.total_operations == 1
        metrics.reset()
        assert metrics.total_operations == 0
        assert metrics.successful_operations == 0
        assert metrics.failed_operations == 0
