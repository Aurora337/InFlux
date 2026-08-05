from influx.kernel.state import State
from influx.kernel.ledger.block import Block


def create_block(height=1):
    return Block(
        height=height,
        previous_hash="0" * 64,
        state_hash=f"state_{height}",
        timestamp=0.0,
    )


def test_identical_states_produce_identical_roots():
    state_a = State()
    state_b = State()

    assert state_a.state_hash == state_b.state_hash


def test_state_root_changes_after_valid_transition():
    state = State()

    initial_root = state.state_hash

    state.apply(create_block())

    assert state.state_hash != initial_root


def test_same_transition_produces_same_root():
    state_a = State()
    state_b = State()

    block = create_block()

    state_a.apply(block)
    state_b.apply(block)

    assert state_a.state_hash == state_b.state_hash


def test_invalid_transition_does_not_change_root():
    state = State()

    original_root = state.state_hash

    invalid_block = Block(
        height=-1,
        previous_hash="bad",
        state_hash="invalid",
        timestamp=0.0,
    )

    try:
        state.apply(invalid_block)
    except ValueError:
        pass

    assert state.state_hash == original_root


def test_state_root_detects_state_corruption():
    state = State()

    state.apply(create_block())

    valid_root = state.state_hash

    state.height = 999

    corrupted_root = state.compute_hash()

    assert corrupted_root != valid_root