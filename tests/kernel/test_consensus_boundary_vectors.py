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
    return state.state_hash


def test_identical_validators_produce_identical_commitments():
    blocks = [
        create_block(1),
        create_block(2),
        create_block(3),
    ]

    validator_a = replay(blocks)
    validator_b = replay(blocks)

    assert validator_a == validator_b


def test_three_validator_consensus_agreement():
    blocks = [
        create_block(1),
        create_block(2),
        create_block(3),
        create_block(4),
    ]

    commitments = [replay(blocks) for _ in range(3)]

    assert len(set(commitments)) == 1


def test_corrupted_validator_is_detectable():
    honest = [
        create_block(1),
        create_block(2),
        create_block(3),
    ]

    corrupted = [
        create_block(1),
        create_block(2, state_hash="CORRUPTED"),
        create_block(3),
    ]

    honest_root = replay(honest)
    corrupted_root = replay(corrupted)

    assert honest_root != corrupted_root


def test_missing_transition_breaks_consensus():
    validator_a = [
        create_block(1),
        create_block(2),
        create_block(3),
    ]

    validator_b = [
        create_block(1),
        create_block(3),
    ]

    assert replay(validator_a) != replay(validator_b)


def test_transition_order_breaks_consensus():
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


def test_consensus_replay_is_stable():
    blocks = [
        create_block(1),
        create_block(2),
        create_block(3),
        create_block(4),
    ]

    first = [replay(blocks) for _ in range(3)]
    second = [replay(blocks) for _ in range(3)]

    assert first == second