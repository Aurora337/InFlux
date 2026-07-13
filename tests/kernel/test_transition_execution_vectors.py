from influx.kernel.state import State
from influx.kernel.ledger.block import Block


def create_test_block(height=1, state_hash="transition_state"):
    return Block(
        height=height,
        previous_hash="0" * 64,
        state_hash=state_hash,
        timestamp=0.0,
    )


def test_transition_execution_is_deterministic():
    state_a = State()
    state_b = State()

    block = create_test_block()

    state_a.apply(block)
    state_b.apply(block)

    assert state_a.state_hash == state_b.state_hash


def test_replaying_same_transition_is_deterministic():
    state = State()

    block = create_test_block()

    state.apply(block)

    first_hash = state.state_hash

    state.apply(block)

    second_hash = state.state_hash

    assert first_hash == second_hash


def test_different_transition_inputs_change_state_commitment():
    state_a = State()
    state_b = State()

    block_a = create_test_block(
        height=1,
        state_hash="state_a",
    )

    block_b = create_test_block(
        height=2,
        state_hash="state_b",
    )

    state_a.apply(block_a)
    state_b.apply(block_b)

    assert state_a.state_hash != state_b.state_hash


def test_state_height_advances_deterministically():
    state = State()

    blocks = [
        create_test_block(height=1),
        create_test_block(height=2),
        create_test_block(height=3),
    ]

    for block in blocks:
        state.apply(block)

    assert state.height == 3


def test_invalid_transition_reference_is_detectable():
    state = State()

    block = Block(
        height=-1,
        previous_hash="bad_hash",
        state_hash="invalid",
        timestamp=0.0,
    )

    try:
        state.apply(block)
    except Exception:
        assert True
    else:
        assert False