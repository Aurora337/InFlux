from influx.kernel.state import State
from influx.kernel.ledger.block import Block


def create_block(height: int, state_hash: str | None = None) -> Block:
    return Block(
        height=height,
        previous_hash="0" * 64,
        state_hash=state_hash or f"state_{height}",
        timestamp=0.0,
    )


def replay(blocks):
    state = State()

    for block in blocks:
        state.apply(block)

    return state


def test_100_block_ledger_is_deterministic():
    blocks = [create_block(i) for i in range(1, 101)]

    state = replay(blocks)

    assert state.height == 100

    replay_state = replay(blocks)

    assert state.state_hash == replay_state.state_hash


def test_1000_block_ledger_is_deterministic():
    blocks = [create_block(i) for i in range(1, 1001)]

    state = replay(blocks)

    assert state.height == 1000

    replay_state = replay(blocks)

    assert state.state_hash == replay_state.state_hash


def test_large_ledger_replay_matches_original():
    blocks = [create_block(i) for i in range(1, 501)]

    original = replay(blocks)

    replayed = replay(blocks)

    assert original.state_hash == replayed.state_hash


def test_duplicate_block_does_not_change_commitment():
    blocks = [create_block(i) for i in range(1, 51)]

    state = replay(blocks)

    original_hash = state.state_hash

    state.apply(blocks[-1])

    assert state.state_hash == original_hash


def test_corrupted_block_changes_commitment():
    honest = [create_block(i) for i in range(1, 51)]

    corrupted = honest.copy()

    corrupted[25] = Block(
        height=26,
        previous_hash="0" * 64,
        state_hash="CORRUPTED_STATE",
        timestamp=0.0,
    )

    honest_state = replay(honest)

    corrupted_state = replay(corrupted)

    assert honest_state.state_hash != corrupted_state.state_hash


def test_multiple_stress_replays_are_identical():
    blocks = [create_block(i) for i in range(1, 201)]

    roots = []

    for _ in range(5):
        roots.append(replay(blocks).state_hash)

    assert len(set(roots)) == 1