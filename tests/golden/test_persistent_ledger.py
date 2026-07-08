"""Integration test for persistent block ledger."""

import sys
import os
import shutil
sys.path.insert(0, "src")

from influx.kernel.ledger.block import Block
from influx.kernel.ledger.block_store import BlockStore


def test_block_creation():
    """Test that blocks can be created and linked."""
    block0 = Block.genesis("hash0")
    assert block0.height == 0
    assert block0.previous_hash == "0" * 64
    assert block0.state_hash == "hash0"
    
    block1 = Block(
        height=1,
        previous_hash=block0.state_hash,
        state_hash="hash1",
        timestamp=12345.0,
    )
    assert block1.height == 1
    assert block1.previous_hash == "hash0"


def test_block_store_persistence():
    """Test that blocks are persisted to disk and reloaded."""
    test_dir = "data/blocks_test"
    
    # Clean up any existing test data
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    # Create store and append blocks
    store = BlockStore(test_dir)
    
    store.append("hash1_state")
    store.append("hash2_state")
    store.append("hash3_state")
    
    assert store.chain_height() == 3
    assert store.verify_chain()
    
    # Reload from disk
    store_reloaded = BlockStore(test_dir)
    assert store_reloaded.chain_height() == 3
    assert store_reloaded.verify_chain()
    
    # Verify chain integrity
    reloaded_block1 = store_reloaded.get_block(0)
    reloaded_block2 = store_reloaded.get_block(1)
    reloaded_block3 = store_reloaded.get_block(2)
    
    assert reloaded_block1.state_hash == "hash1_state"
    assert reloaded_block2.previous_hash == reloaded_block1.state_hash
    assert reloaded_block3.previous_hash == reloaded_block2.state_hash
    
    # Clean up
    shutil.rmtree(test_dir)


def test_block_chain_verification():
    """Test that valid chains pass verification."""
    test_dir = "data/blocks_verify_test"
    
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    store = BlockStore(test_dir)
    store.append("hash1_state")
    store.append("hash2_state")
    store.append("hash3_state")
    
    # Valid chain should pass verification
    assert store.verify_chain()
    
    # Verify links are correct
    assert store.get_block(1).previous_hash == store.get_block(0).state_hash
    assert store.get_block(2).previous_hash == store.get_block(1).state_hash
    
    # Clean up
    shutil.rmtree(test_dir)
