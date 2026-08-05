from influx.kernel.state import State
from influx.kernel.ledger.block import Block

def create_test_block(height: int = 1) -> Block:
    return Block(
        height=height,
        previous_hash="0" * 64,
        state_hash="test_state_hash",
        timestamp=0.0,
    )


def test_same_state_same_block_produces_same_hash():
    state_a = State()
    state_b = State()

    block = create_test_block()

    state_a.apply(block)
    state_b.apply(block)

    assert state_a.state_hash == state_b.state_hash


def test_different_transitions_produce_different_hashes():
    state_a = State()
    state_b = State()

    block_a = create_test_block(height=1)
    block_b = create_test_block(height=2)

    state_a.apply(block_a)
    state_b.apply(block_b)

    assert state_a.state_hash != state_b.state_hash


def test_replay_produces_identical_state_commitment():
    original = State()

    blocks = [
        create_test_block(1),
        create_test_block(2),
        create_test_block(3),
    ]

    for block in blocks:
        original.apply(block)

    replay = State()

    for block in blocks:
        replay.apply(block)

    assert original.state_hash == replay.state_hash


def test_state_transition_height_is_deterministic():
    state = State()

    blocks = [
        create_test_block(1),
        create_test_block(2),
        create_test_block(3),
    ]

    for block in blocks:
        state.apply(block)

    assert state.height == 3


def test_state_hash_changes_after_transition():
    state = State()

    initial_hash = state.state_hash

    state.apply(create_test_block())

    assert state.state_hash != initial_hash