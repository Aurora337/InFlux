"""
Unit tests for Economic Context.
"""

import pytest
from influx.economics.economic_context import EconomicContext, create_economic_context


class TestEconomicContext:
    """Test EconomicContext class."""

    def test_create_context_default(self):
        """Test creating a context with defaults."""
        ctx = create_economic_context(block_height=0)
        assert ctx.block_height == 0
        assert ctx.state_root == ""
        assert ctx.previous_state_root == ""
        assert ctx.block_timestamp is not None
        assert ctx.epoch == 0

    def test_create_context_with_values(self):
        """Test creating a context with all values."""
        ctx = create_economic_context(
            block_height=100,
            block_timestamp=1234567890,
            state_root="abc123",
            epoch=5,
            previous_state_root="def456",
        )
        assert ctx.block_height == 100
        assert ctx.block_timestamp == 1234567890
        assert ctx.state_root == "abc123"
        assert ctx.epoch == 5
        assert ctx.previous_state_root == "def456"

    def test_context_snapshot(self):
        """Test context snapshot."""
        ctx = create_economic_context(
            block_height=50,
            block_timestamp=1000,
            state_root="root_hash",
            epoch=3,
        )
        snap = ctx.snapshot()
        assert snap["block_height"] == 50
        assert snap["block_timestamp"] == 1000
        assert snap["state_root"] == "root_hash"
        assert snap["epoch"] == 3

    def test_context_determinism(self):
        """Test that same inputs produce same context."""
        ctx1 = create_economic_context(
            block_height=100,
            block_timestamp=5000,
            state_root="abc",
        )
        ctx2 = create_economic_context(
            block_height=100,
            block_timestamp=5000,
            state_root="abc",
        )
        assert ctx1.block_height == ctx2.block_height
        assert ctx1.block_timestamp == ctx2.block_timestamp
        assert ctx1.state_root == ctx2.state_root
