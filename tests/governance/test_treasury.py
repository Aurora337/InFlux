"""
Unit tests for the governance treasury module.

Tests treasury initialization, deposit/withdraw operations, dispersal lifecycle,
accounting, multi-token support, and snapshot behavior.
"""

import pytest

from influx.governance.treasury import Treasury, Dispersal, DispersalStatus


class TestTreasuryInitialization:
    """Treasury initialization and default state tests."""

    def test_default_treasury(self):
        """Default treasury should have INFLUX token with zero balance."""
        treasury = Treasury()
        assert treasury.treasury_id == "main"
        assert treasury.balances == {"INFLUX": 0.0}
        assert treasury.total_dispersed == {"INFLUX": 0.0}
        assert treasury.total_deposited == {"INFLUX": 0.0}
        assert treasury.dispersals == {}

    def test_treasury_with_custom_id(self):
        """Treasury can be created with a custom ID."""
        treasury = Treasury(treasury_id="community-pool")
        assert treasury.treasury_id == "community-pool"


class TestTreasuryDeposit:
    """Treasury deposit operations tests."""

    def test_deposit_valid_amount(self):
        """Deposit a valid positive amount."""
        treasury = Treasury()
        assert treasury.deposit("INFLUX", 1000.0, "minter") is True
        assert treasury.get_balance("INFLUX") == 1000.0
        assert treasury.total_deposited["INFLUX"] == 1000.0

    def test_deposit_zero_rejected(self):
        """Deposit of zero should be rejected."""
        treasury = Treasury()
        assert treasury.deposit("INFLUX", 0.0, "minter") is False
        assert treasury.get_balance("INFLUX") == 0.0

    def test_deposit_negative_rejected(self):
        """Deposit of negative amount should be rejected."""
        treasury = Treasury()
        assert treasury.deposit("INFLUX", -100.0, "minter") is False
        assert treasury.get_balance("INFLUX") == 0.0

    def test_deposit_new_token(self):
        """Deposit creates new token balance if it doesn't exist."""
        treasury = Treasury()
        assert treasury.deposit("USDC", 5000.0, "bridge") is True
        assert treasury.get_balance("USDC") == 5000.0
        assert treasury.total_deposited["USDC"] == 5000.0
        assert treasury.total_dispersed["USDC"] == 0.0

    def test_multiple_deposits(self):
        """Multiple deposits should accumulate."""
        treasury = Treasury()
        treasury.deposit("INFLUX", 100.0, "minter")
        treasury.deposit("INFLUX", 200.0, "minter")
        treasury.deposit("INFLUX", 300.0, "minter")
        assert treasury.get_balance("INFLUX") == 600.0
        assert treasury.total_deposited["INFLUX"] == 600.0


class TestTreasuryWithdraw:
    """Treasury withdraw operations tests."""

    def test_withdraw_valid_amount(self):
        """Withdraw a valid positive amount."""
        treasury = Treasury()
        treasury.deposit("INFLUX", 1000.0, "minter")
        assert treasury.withdraw("INFLUX", 400.0, "alice") is True
        assert treasury.get_balance("INFLUX") == 600.0
        assert treasury.total_dispersed["INFLUX"] == 400.0

    def test_withdraw_insufficient_funds(self):
        """Withdraw more than balance should be rejected."""
        treasury = Treasury()
        treasury.deposit("INFLUX", 100.0, "minter")
        assert treasury.withdraw("INFLUX", 200.0, "alice") is False
        assert treasury.get_balance("INFLUX") == 100.0

    def test_withdraw_zero_rejected(self):
        """Withdraw of zero should be rejected."""
        treasury = Treasury()
        treasury.deposit("INFLUX", 100.0, "minter")
        assert treasury.withdraw("INFLUX", 0.0, "alice") is False

    def test_withdraw_negative_rejected(self):
        """Withdraw of negative amount should be rejected."""
        treasury = Treasury()
        treasury.deposit("INFLUX", 100.0, "minter")
        assert treasury.withdraw("INFLUX", -50.0, "alice") is False

    def test_withdraw_unknown_token(self):
        """Withdraw from unknown token should be rejected."""
        treasury = Treasury()
        assert treasury.withdraw("UNKNOWN", 100.0, "alice") is False

    def test_exact_balance_withdraw(self):
        """Withdraw exactly the full balance."""
        treasury = Treasury()
        treasury.deposit("INFLUX", 500.0, "minter")
        assert treasury.withdraw("INFLUX", 500.0, "alice") is True
        assert treasury.get_balance("INFLUX") == 0.0
        assert treasury.total_dispersed["INFLUX"] == 500.0


class TestTreasuryDispersal:
    """Treasury dispersal lifecycle tests."""

    def test_create_dispersal_valid(self):
        """Create a valid dispersal request."""
        treasury = Treasury()
        treasury.deposit("INFLUX", 1000.0, "minter")
        dispersal = treasury.create_dispersal(
            proposal_id="prop-001",
            recipient="alice",
            amount=500.0,
            token="INFLUX",
            reason="Community grant",
        )
        assert dispersal is not None
        assert dispersal.proposal_id == "prop-001"
        assert dispersal.recipient == "alice"
        assert dispersal.amount == 500.0
        assert dispersal.status == DispersalStatus.PENDING
        assert dispersal.dispersal_id is not None

    def test_create_dispersal_insufficient_funds(self):
        """Create dispersal with insufficient funds should return None."""
        treasury = Treasury()
        treasury.deposit("INFLUX", 100.0, "minter")
        dispersal = treasury.create_dispersal(
            proposal_id="prop-001",
            recipient="alice",
            amount=500.0,
            token="INFLUX",
            reason="Over budget",
        )
        assert dispersal is None

    def test_create_dispersal_zero_amount(self):
        """Create dispersal with zero amount should return None."""
        treasury = Treasury()
        treasury.deposit("INFLUX", 1000.0, "minter")
        dispersal = treasury.create_dispersal(
            proposal_id="prop-001",
            recipient="alice",
            amount=0.0,
            token="INFLUX",
            reason="Zero amount",
        )
        assert dispersal is None

    def test_create_dispersal_unknown_token(self):
        """Create dispersal with unknown token should return None."""
        treasury = Treasury()
        dispersal = treasury.create_dispersal(
            proposal_id="prop-001",
            recipient="alice",
            amount=100.0,
            token="UNKNOWN",
            reason="Unknown token",
        )
        assert dispersal is None

    def test_dispersal_approve(self):
        """Approve a pending dispersal."""
        treasury = Treasury()
        treasury.deposit("INFLUX", 1000.0, "minter")
        dispersal = treasury.create_dispersal("prop-001", "alice", 500.0, "INFLUX", "Grant")
        assert treasury.approve_dispersal(dispersal.dispersal_id) is True
        assert treasury.dispersals[dispersal.dispersal_id].status == DispersalStatus.APPROVED

    def test_dispersal_approve_nonexistent(self):
        """Approve a non-existent dispersal should fail."""
        treasury = Treasury()
        assert treasury.approve_dispersal("nonexistent") is False

    def test_dispersal_approve_already_approved(self):
        """Approve already approved dispersal should fail."""
        treasury = Treasury()
        treasury.deposit("INFLUX", 1000.0, "minter")
        dispersal = treasury.create_dispersal("prop-001", "alice", 500.0, "INFLUX", "Grant")
        treasury.approve_dispersal(dispersal.dispersal_id)
        assert treasury.approve_dispersal(dispersal.dispersal_id) is False

    def test_dispersal_full_lifecycle(self):
        """Complete dispersal lifecycle: PENDING -> APPROVED -> EXECUTED."""
        treasury = Treasury()
        treasury.deposit("INFLUX", 1000.0, "minter")

        # Create
        dispersal = treasury.create_dispersal("prop-001", "alice", 500.0, "INFLUX", "Grant")
        assert dispersal.status == DispersalStatus.PENDING

        # Approve
        treasury.approve_dispersal(dispersal.dispersal_id)
        assert treasury.dispersals[dispersal.dispersal_id].status == DispersalStatus.APPROVED

        # Execute
        assert treasury.execute_dispersal(dispersal.dispersal_id) is True
        assert treasury.dispersals[dispersal.dispersal_id].status == DispersalStatus.EXECUTED
        assert treasury.get_balance("INFLUX") == 500.0  # 1000 - 500
        assert treasury.total_dispersed["INFLUX"] == 500.0

    def test_dispersal_execute_not_approved(self):
        """Execute a non-approved dispersal should fail."""
        treasury = Treasury()
        treasury.deposit("INFLUX", 1000.0, "minter")
        dispersal = treasury.create_dispersal("prop-001", "alice", 500.0, "INFLUX", "Grant")
        # Try to execute without approval
        assert treasury.execute_dispersal(dispersal.dispersal_id) is False
        assert dispersal.status == DispersalStatus.PENDING

    def test_dispersal_execute_nonexistent(self):
        """Execute a non-existent dispersal should fail."""
        treasury = Treasury()
        assert treasury.execute_dispersal("nonexistent") is False

    def test_dispersal_hash_determinism(self):
        """Same dispersal fields should produce the same hash."""
        from influx.governance.treasury import Dispersal

        d1 = Dispersal(
            dispersal_id="disp-001",
            proposal_id="prop-001",
            recipient="alice",
            amount=500.0,
            token="INFLUX",
            reason="Grant",
        )
        d2 = Dispersal(
            dispersal_id="disp-001",
            proposal_id="prop-001",
            recipient="alice",
            amount=500.0,
            token="INFLUX",
            reason="Grant",
        )
        assert d1.hash == d2.hash

    def test_dispersal_snapshot(self):
        """Dispersal snapshot should contain all expected fields."""
        treasury = Treasury()
        treasury.deposit("INFLUX", 1000.0, "minter")
        dispersal = treasury.create_dispersal("prop-001", "alice", 500.0, "INFLUX", "Grant")
        treasury.approve_dispersal(dispersal.dispersal_id)

        snap = dispersal.snapshot()
        assert snap["dispersal_id"] == dispersal.dispersal_id
        assert snap["proposal_id"] == "prop-001"
        assert snap["recipient"] == "alice"
        assert snap["amount"] == 500.0
        assert snap["token"] == "INFLUX"
        assert snap["status"] == "approved"
        assert snap["hash"] == dispersal.hash


class TestMultiToken:
    """Multi-token treasury support tests."""

    def test_multiple_tokens(self):
        """Treasury should support multiple tokens independently."""
        treasury = Treasury()
        treasury.deposit("INFLUX", 1000.0, "minter")
        treasury.deposit("USDC", 5000.0, "bridge")
        treasury.deposit("ETH", 10.0, "bridge")

        assert treasury.get_balance("INFLUX") == 1000.0
        assert treasury.get_balance("USDC") == 5000.0
        assert treasury.get_balance("ETH") == 10.0

    def test_token_independence(self):
        """Operations on different tokens should not interfere."""
        treasury = Treasury()
        treasury.deposit("INFLUX", 1000.0, "minter")
        treasury.deposit("USDC", 5000.0, "bridge")

        treasury.withdraw("INFLUX", 500.0, "alice")
        assert treasury.get_balance("INFLUX") == 500.0
        assert treasury.get_balance("USDC") == 5000.0  # Unchanged
        assert treasury.total_dispersed["INFLUX"] == 500.0
        assert treasury.total_dispersed["USDC"] == 0.0


class TestTreasurySnapshot:
    """Treasury snapshot tests."""

    def test_treasury_snapshot_empty(self):
        """Empty treasury snapshot should reflect default state."""
        treasury = Treasury()
        snap = treasury.snapshot()
        assert snap["treasury_id"] == "main"
        assert snap["balances"] == {"INFLUX": 0.0}
        assert snap["total_dispersed"] == {"INFLUX": 0.0}
        assert snap["total_deposited"] == {"INFLUX": 0.0}
        assert snap["dispersal_count"] == 0
        assert snap["pending_dispersals"] == 0

    def test_treasury_snapshot_with_activity(self):
        """Treasury snapshot should reflect all activity."""
        treasury = Treasury()
        treasury.deposit("INFLUX", 2000.0, "minter")
        treasury.deposit("USDC", 10000.0, "bridge")
        dispersal = treasury.create_dispersal("prop-001", "alice", 500.0, "INFLUX", "Grant")
        treasury.approve_dispersal(dispersal.dispersal_id)
        treasury.execute_dispersal(dispersal.dispersal_id)

        snap = treasury.snapshot()
        assert snap["balances"]["INFLUX"] == 1500.0  # 2000 - 500
        assert snap["balances"]["USDC"] == 10000.0
        assert snap["total_deposited"]["INFLUX"] == 2000.0
        assert snap["total_dispersed"]["INFLUX"] == 500.0
        assert snap["dispersal_count"] == 1
        assert snap["pending_dispersals"] == 0
