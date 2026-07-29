"""
Unit tests for Economic Scheduler (current API).
"""

from influx.economics.economic_scheduler import EconomicScheduler, ScheduledOperation
from influx.economics.economic_executor import EconomicOperation, OperationType


class TestScheduledOperation:
    def test_create_and_hash_snapshot(self):
        op = EconomicOperation(OperationType.MINT, "", "addr_001", 1000.0)
        scheduled = ScheduledOperation(
            operation=op,
            target_block_height=100,
            scheduled_at_block=50,
            description="Mint tokens",
        )
        assert scheduled.operation == op
        assert scheduled.target_block_height == 100
        assert scheduled.scheduled_at_block == 50
        assert len(scheduled.hash) == 64
        snap = scheduled.snapshot()
        assert snap["target_block_height"] == 100
        assert snap["description"] == "Mint tokens"


class TestEconomicScheduler:
    def test_schedule_and_pending_counts(self):
        scheduler = EconomicScheduler()
        op = EconomicOperation(OperationType.MINT, "", "addr_001", 1000.0)
        ok = scheduler.schedule(op, target_block_height=100, current_block_height=50, description="Test mint")
        assert ok is True
        assert scheduler.get_schedule_count() == 1
        assert scheduler.get_pending_count() == 1

    def test_reject_invalid_schedule(self):
        scheduler = EconomicScheduler()
        op_bad_amt = EconomicOperation(OperationType.MINT, "", "addr_001", 0.0)
        assert scheduler.schedule(op_bad_amt, 100, 50) is False

        op = EconomicOperation(OperationType.MINT, "", "addr_001", 1.0)
        assert scheduler.schedule(op, 50, 50) is False  # cannot schedule in past/current block

    def test_due_order_and_replay_determinism(self):
        scheduler = EconomicScheduler()
        op1 = EconomicOperation(OperationType.MINT, "", "addr_001", 10.0)
        op2 = EconomicOperation(OperationType.TRANSFER, "addr_001", "addr_002", 5.0)
        op3 = EconomicOperation(OperationType.BURN, "addr_001", "", 2.0)

        scheduler.schedule(op1, 100, 10)
        scheduler.schedule(op2, 120, 10)
        scheduler.schedule(op3, 100, 10)

        due_100 = scheduler.get_due_operations(100)
        assert [o.operation_type for o in due_100] == [OperationType.MINT, OperationType.BURN]

        # same call should not duplicate completed operations
        due_100_again = scheduler.get_due_operations(100)
        assert due_100_again == []

        due_all_120 = scheduler.get_all_due_operations(120)
        assert [o.operation_type for o in due_all_120] == [OperationType.TRANSFER]

    def test_scheduled_blocks_snapshot_and_reset(self):
        scheduler = EconomicScheduler()
        op = EconomicOperation(OperationType.MINT, "", "addr_001", 1000.0)
        scheduler.schedule(op, 100, 50)
        scheduler.schedule(op, 200, 50)

        assert scheduler.get_scheduled_blocks() == [100, 200]
        snap = scheduler.snapshot()
        assert snap["schedule_count"] == 2
        assert snap["pending_count"] >= 1
        assert "scheduled_blocks" in snap

        scheduler.reset()
        assert scheduler.get_schedule_count() == 0
        assert scheduler.get_pending_count() == 0
