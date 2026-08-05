"""
Unit tests for Economic Transition (current API).
"""

from influx.economics.economic_transition import EconomicTransition, TransitionType
from influx.economics.economic_state import EconomicState


class TestEconomicTransition:
    def _state(self):
        s = EconomicState()
        s.get_account("addr_001").balances["INFLUX"] = 500.0
        s.get_account("addr_002").balances["INFLUX"] = 0.0
        s.supply.total_supply = 500.0
        s.supply.circulating_supply = 500.0
        s.update_state_root()
        return s

    def test_transition_type_values(self):
        values = [t.value for t in TransitionType]
        assert len(values) == len(set(values))

    def test_apply_transfer(self):
        engine = EconomicTransition()
        state = self._state()
        t = engine.apply_transfer(state, "addr_001", "addr_002", 100.0, block_height=1)
        assert t is not None
        assert state.get_balance("addr_001") == 400.0
        assert state.get_balance("addr_002") == 100.0

    def test_apply_transfer_insufficient(self):
        engine = EconomicTransition()
        state = self._state()
        t = engine.apply_transfer(state, "addr_001", "addr_002", 10000.0, block_height=1)
        assert t is None

    def test_apply_mint_and_burn(self):
        engine = EconomicTransition()
        state = self._state()
        tm = engine.apply_mint(state, "addr_001", 100.0, block_height=1)
        tb = engine.apply_burn(state, "addr_001", 50.0, block_height=1)
        assert tm is not None and tb is not None
        assert state.get_balance("addr_001") == 550.0
        assert state.supply.total_supply == 550.0

    def test_apply_lock_unlock(self):
        engine = EconomicTransition()
        state = self._state()
        tl = engine.apply_lock(state, "addr_001", 200.0, block_height=1)
        tu = engine.apply_unlock(state, "addr_001", 100.0, block_height=2)
        assert tl is not None and tu is not None
        assert state.get_account("addr_001").locked_balances.get("INFLUX", 0.0) == 100.0

    def test_advance_epoch(self):
        engine = EconomicTransition()
        state = self._state()
        prev = state.current_epoch
        t = engine.advance_epoch(state, block_height=10)
        assert t is not None
        assert state.current_epoch == prev + 1

    def test_snapshot_and_reset(self):
        engine = EconomicTransition()
        state = self._state()
        engine.apply_mint(state, "addr_001", 10.0, block_height=1)
        snap = engine.snapshot()
        assert "transition_count" in snap
        assert "transitions" in snap
        assert engine.get_transition_count() == 1
        engine.reset()
        assert engine.get_transition_count() == 0
