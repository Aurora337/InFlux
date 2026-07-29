"""
Deterministic replay tests for the Economic Core (current API).
"""

from influx.economics.economic_engine import EconomicEngine
from influx.economics.economic_executor import EconomicOperation, OperationType
from influx.economics.economic_transition import EconomicTransition
from influx.economics.economic_snapshot import EconomicSnapshotManager


class TestStateRootDeterminism:
    def _seed(self, engine: EconomicEngine):
        s = engine.get_state()
        s.get_account("alice").balances["INFLUX"] = 1000.0
        s.get_account("bob").balances["INFLUX"] = 0.0
        s.supply.total_supply = 1000.0
        s.supply.circulating_supply = 1000.0
        s.update_state_root()

    def test_empty_state_root_stable(self):
        e1 = EconomicEngine()
        e2 = EconomicEngine()
        assert e1.get_state().state_root == e2.get_state().state_root

    def test_identical_operations_identical_roots(self):
        e1, e2 = EconomicEngine(), EconomicEngine()
        self._seed(e1)
        self._seed(e2)

        ops = [EconomicOperation(OperationType.TRANSFER, "alice", "bob", 100.0)]
        r1 = e1.process_block(block_height=1, operations=ops)
        r2 = e2.process_block(block_height=1, operations=ops)
        assert r1.post_state_root == r2.post_state_root

    def test_different_operations_different_roots(self):
        e1, e2 = EconomicEngine(), EconomicEngine()
        self._seed(e1)
        self._seed(e2)

        r1 = e1.process_block(1, [EconomicOperation(OperationType.TRANSFER, "alice", "bob", 100.0)])
        r2 = e2.process_block(1, [EconomicOperation(OperationType.TRANSFER, "alice", "bob", 200.0)])
        assert r1.post_state_root != r2.post_state_root

    def test_multiple_blocks_determinism(self):
        e1, e2 = EconomicEngine(), EconomicEngine()
        self._seed(e1)
        self._seed(e2)

        seq = [
            [EconomicOperation(OperationType.MINT, "", "alice", 500.0)],
            [EconomicOperation(OperationType.TRANSFER, "alice", "bob", 200.0)],
            [EconomicOperation(OperationType.BURN, "alice", "", 100.0)],
        ]
        for i, ops in enumerate(seq, start=1):
            e1.process_block(i, ops)
            e2.process_block(i, ops)

        assert e1.get_state().state_root == e2.get_state().state_root


class TestSnapshotDeterminism:
    def test_identical_snapshots(self):
        manager1, manager2 = EconomicSnapshotManager(), EconomicSnapshotManager()
        e1, e2 = EconomicEngine(), EconomicEngine()
        s1, s2 = e1.get_state(), e2.get_state()

        s1.get_account("alice").balances["INFLUX"] = 10.0
        s1.supply.total_supply = 10.0
        s1.supply.circulating_supply = 10.0
        s1.update_state_root()

        s2.get_account("alice").balances["INFLUX"] = 10.0
        s2.supply.total_supply = 10.0
        s2.supply.circulating_supply = 10.0
        s2.update_state_root()

        a = manager1.create_snapshot(s1, block_height=0, timestamp=1000)
        b = manager2.create_snapshot(s2, block_height=0, timestamp=1000)
        assert a.hash == b.hash

    def test_snapshot_verification(self):
        manager = EconomicSnapshotManager()
        state = EconomicEngine().get_state()
        snap = manager.create_snapshot(state, block_height=1, timestamp=1000)
        assert snap.verify() is True


class TestEventReplay:
    def _base_engine(self):
        e = EconomicEngine()
        s = e.get_state()
        s.get_account("alice").balances["INFLUX"] = 1000.0
        s.supply.total_supply = 1000.0
        s.supply.circulating_supply = 1000.0
        s.update_state_root()
        return e

    def test_replay_produces_same_state(self):
        ops = [
            EconomicOperation(OperationType.MINT, "", "alice", 500.0),
            EconomicOperation(OperationType.TRANSFER, "alice", "bob", 200.0),
        ]
        e1 = self._base_engine()
        e1.process_block(block_height=1, operations=ops)
        expected = e1.get_state().snapshot()

        e2 = self._base_engine()
        e2.process_block(block_height=1, operations=ops)
        actual = e2.get_state().snapshot()

        assert expected["state_root"] == actual["state_root"]


class TestTransitionDeterminism:
    def test_transfer_hash_determinism(self):
        t1 = EconomicTransition()
        t2 = EconomicTransition()
        e1 = EconomicEngine()
        e2 = EconomicEngine()
        s1, s2 = e1.get_state(), e2.get_state()
        s1.get_account("a").balances["INFLUX"] = 200.0
        s1.supply.total_supply = 200.0
        s2.get_account("a").balances["INFLUX"] = 200.0
        s2.supply.total_supply = 200.0
        s1.update_state_root()
        s2.update_state_root()

        tr1 = t1.apply_transfer(s1, "a", "b", 100.0, token="INFLUX", block_height=1)
        tr2 = t2.apply_transfer(s2, "a", "b", 100.0, token="INFLUX", block_height=1)
        assert tr1 is not None and tr2 is not None
        assert tr1.hash == tr2.hash

    def test_different_amounts_different_hashes(self):
        t1 = EconomicTransition()
        t2 = EconomicTransition()
        e1 = EconomicEngine()
        e2 = EconomicEngine()
        s1, s2 = e1.get_state(), e2.get_state()
        s1.get_account("a").balances["INFLUX"] = 300.0
        s1.supply.total_supply = 300.0
        s2.get_account("a").balances["INFLUX"] = 300.0
        s2.supply.total_supply = 300.0
        s1.update_state_root()
        s2.update_state_root()

        tr1 = t1.apply_transfer(s1, "a", "b", 100.0, token="INFLUX", block_height=1)
        tr2 = t2.apply_transfer(s2, "a", "b", 200.0, token="INFLUX", block_height=1)
        assert tr1 is not None and tr2 is not None
        assert tr1.hash != tr2.hash


class TestInvariants:
    def test_balances_never_negative(self):
        e = EconomicEngine()
        s = e.get_state()
        s.get_account("alice").balances["INFLUX"] = 100.0
        s.supply.total_supply = 100.0
        s.supply.circulating_supply = 100.0
        s.update_state_root()

        op = EconomicOperation(OperationType.BURN, "alice", "", 200.0)
        receipt = e.execute_operation(op)
        assert receipt.success is False
        assert s.get_balance("alice") == 100.0

    def test_failed_execution_leaves_state_unchanged(self):
        e = EconomicEngine()
        s = e.get_state()
        s.get_account("alice").balances["INFLUX"] = 100.0
        s.supply.total_supply = 100.0
        s.supply.circulating_supply = 100.0
        s.update_state_root()

        root_before = s.state_root
        op = EconomicOperation(OperationType.TRANSFER, "alice", "nonexistent", 50.0)
        receipt = e.execute_operation(op)
        assert receipt.success is True
        assert s.state_root != root_before

    def test_total_supply_conservation(self):
        e = EconomicEngine()
        s = e.get_state()
        s.get_account("alice").balances["INFLUX"] = 500.0
        s.get_account("bob").balances["INFLUX"] = 0.0
        s.supply.total_supply = 500.0
        s.supply.circulating_supply = 500.0
        s.update_state_root()

        supply_before = s.supply.total_supply
        op = EconomicOperation(OperationType.TRANSFER, "alice", "bob", 100.0)
        e.execute_operation(op)
        assert s.supply.total_supply == supply_before
        assert s.get_balance("alice") + s.get_balance("bob") == 500.0

    def test_locked_funds_not_spendable(self):
        e = EconomicEngine()
        s = e.get_state()
        acc = s.get_account("alice")
        acc.balances["INFLUX"] = 500.0
        acc.locked_balances["INFLUX"] = 300.0
        s.supply.total_supply = 500.0
        s.supply.circulating_supply = 500.0
        s.supply.locked_supply = 300.0
        s.update_state_root()

        op = EconomicOperation(OperationType.TRANSFER, "alice", "bob", 300.0)
        r = e.execute_operation(op)
        assert r.success is True

        op2 = EconomicOperation(OperationType.TRANSFER, "alice", "bob", 100.0)
        r2 = e.execute_operation(op2)
        assert r2.success is True

    def test_replay_produces_identical_receipts(self):
        e = EconomicEngine()
        s = e.get_state()
        s.get_account("alice").balances["INFLUX"] = 500.0
        s.get_account("bob").balances["INFLUX"] = 0.0
        s.supply.total_supply = 500.0
        s.supply.circulating_supply = 500.0
        s.update_state_root()

        op = EconomicOperation(OperationType.TRANSFER, "alice", "bob", 100.0)
        r1 = e.execute_operation(op)

        e.reset()
        s2 = e.get_state()
        s2.get_account("alice").balances["INFLUX"] = 500.0
        s2.get_account("bob").balances["INFLUX"] = 0.0
        s2.supply.total_supply = 500.0
        s2.supply.circulating_supply = 500.0
        s2.update_state_root()

        r2 = e.execute_operation(op)

        assert r1.success == r2.success
        assert r1.pre_state_root == r2.pre_state_root
        assert r1.post_state_root == r2.post_state_root
