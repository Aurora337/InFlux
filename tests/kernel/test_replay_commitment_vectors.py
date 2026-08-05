from influx.kernel.state import State
from influx.kernel.ledger.block import Block


def create_block(height: int) -> Block:
    return Block(
        height=height,
        previous_hash="0" * 64,
        state_hash=f"state_{height}",
        timestamp=0.0,
    )


def replay(blocks):
    state = State()
    for block in blocks:
        state.apply(block)
    return state.state_hash


def test_same_transition_sequence_produces_same_commitment():
    blocks = [
        create_block(1),
        create_block(2),
        create_block(3),
    ]

    assert replay(blocks) == replay(blocks)


def test_modified_transition_changes_commitment():
    original = [
        create_block(1),
        create_block(2),
        create_block(3),
    ]

    modified = [
        create_block(1),
        Block(
            height=2,
            previous_hash="0" * 64,
            state_hash="modified_state",
            timestamp=0.0,
        ),
        create_block(3),
    ]

    assert replay(original) != replay(modified)


def test_missing_transition_changes_commitment():
    full = [
        create_block(1),
        create_block(2),
        create_block(3),
    ]

    missing = [
        create_block(1),
        create_block(3),
    ]

    assert replay(full) != replay(missing)


def test_transition_order_changes_commitment():
    ordered = [
        create_block(1),
        create_block(2),
        create_block(3),
    ]

    reordered = [
        create_block(1),
        create_block(3),
        create_block(2),
    ]

    assert replay(ordered) != replay(reordered)


def test_repeated_replay_is_stable():
    blocks = [
        create_block(1),
        create_block(2),
        create_block(3),
        create_block(4),
    ]

    root1 = replay(blocks)
    root2 = replay(blocks)
    root3 = replay(blocks)

    assert root1 == root2 == root3