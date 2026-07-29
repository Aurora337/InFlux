"""
Unit tests for Economic Snapshot (current API).
"""

from influx.economics.economic_snapshot import EconomicSnapshotManager
from influx.economics.economic_state import EconomicState


class TestEconomicSnapshot:
    def _state(self):
        s = EconomicState()
        s.get_account("addr_001").balances["INFLUX"] = 100.0
        s.supply.total_supply = 100.0
        s.supply.circulating_supply = 100.0
        s.update_state_root()
        return s

    def test_identical_state_identical_snapshot(self):
        m1 = EconomicSnapshotManager()
        m2 = EconomicSnapshotManager()
        s1 = self._state()
        s2 = self._state()

        a = m1.create_snapshot(s1, block_height=10, timestamp=1234567890)
        b = m2.create_snapshot(s2, block_height=10, timestamp=1234567890)

        assert a.snapshot_id == b.snapshot_id
        assert a.hash == b.hash
        assert a.snapshot() == b.snapshot()

    def test_snapshot_hash_stability_and_serialization_determinism(self):
        m = EconomicSnapshotManager()
        s = self._state()
        snap = m.create_snapshot(s, block_height=7, timestamp=111)

        h1 = snap.hash
        h2 = snap.compute_hash()
        assert h1 == h2
        assert snap.verify() is True

        ser1 = snap.snapshot()
        ser2 = snap.snapshot()
        assert ser1 == ser2


class TestEconomicSnapshotManager:
    def _state(self):
        s = EconomicState()
        s.get_account("addr_001").balances["INFLUX"] = 50.0
        s.supply.total_supply = 50.0
        s.supply.circulating_supply = 50.0
        s.update_state_root()
        return s

    def test_create_retrieve_and_equality(self):
        manager = EconomicSnapshotManager()
        state = self._state()
        created = manager.create_snapshot(state, 0, timestamp=1000)
        by_id = manager.get_snapshot(created.snapshot_id)
        by_height = manager.get_snapshot_by_height(0)

        assert by_id is not None
        assert by_height is not None
        assert by_id.snapshot() == created.snapshot()
        assert by_height.snapshot() == created.snapshot()

    def test_verify_against_state_and_restore_pattern(self):
        manager = EconomicSnapshotManager()
        state = self._state()
        created = manager.create_snapshot(state, 5, timestamp=2000)

        assert manager.verify_snapshot(created.snapshot_id) is True
        assert manager.verify_snapshot_against_state(created.snapshot_id, state) is True

        # mutate state => verification against original snapshot must fail
        state.get_account("addr_001").balances["INFLUX"] = 60.0
        state.supply.total_supply = 60.0
        state.supply.circulating_supply = 60.0
        state.update_state_root()
        assert manager.verify_snapshot_against_state(created.snapshot_id, state) is False

    def test_manager_snapshot_and_reset(self):
        manager = EconomicSnapshotManager()
        state = self._state()
        manager.create_snapshot(state, 0, timestamp=1000)
        manager.create_snapshot(state, 1, timestamp=1001)

        snap = manager.snapshot()
        assert snap["snapshot_count"] == 2
        assert snap["snapshot_heights"] == [0, 1]
        assert snap["latest_snapshot"]["block_height"] == 1

        manager.reset()
        assert manager.get_snapshot_count() == 0
