"""
Unit tests for Economic State (current API).
"""

from influx.economics.economic_state import EconomicState


class TestEconomicState:
    def test_initial_state(self):
        state = EconomicState()
        state.update_state_root()
        assert state.state_root is not None
        assert len(state.state_root) == 64
        assert state.current_epoch == 0
        assert state.blocks_since_epoch_start == 0

    def test_get_account_creates_on_access(self):
        state = EconomicState()
        account = state.get_account("addr_001")
        assert account.address == "addr_001"
        assert state.has_account("addr_001") is True
        assert state.get_balance("addr_001") == 0.0

    def test_balances_and_snapshot(self):
        state = EconomicState()
        state.get_account("addr_001").balances["INFLUX"] = 100.0
        state.supply.total_supply = 100.0
        state.supply.circulating_supply = 100.0
        state.update_state_root()
        snap = state.snapshot()
        assert snap["account_count"] == 1
        assert snap["current_epoch"] == 0
        assert "state_root" in snap

    def test_clone(self):
        state = EconomicState()
        state.get_account("addr_001").balances["INFLUX"] = 123.0
        state.supply.total_supply = 123.0
        cloned = state.clone()
        assert cloned.get_balance("addr_001") == 123.0
        assert cloned.supply.total_supply == 123.0

    def test_verify_invariants(self):
        state = EconomicState()
        state.supply.total_supply = -1.0
        violations = state.verify_invariants()
        assert any("negative" in v.lower() for v in violations)

    def test_reset(self):
        state = EconomicState()
        state.get_account("addr_001").balances["INFLUX"] = 50.0
        state.supply.total_supply = 50.0
        state.reset()
        assert state.supply.total_supply == 0.0
        assert state.accounts == {}
