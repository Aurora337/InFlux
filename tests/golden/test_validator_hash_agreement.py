from influx.kernel.state import State
from influx.kernel.ledger.pipeline import process_pipeline
from influx.kernel.ledger.serialization import serialize_state
from influx.kernel.ledger.hash_sync import compute_root_hash


def test_validator_hash_agreement():
    state = State(epoch=0, supply=1000.0, participants=100)
    next_state = process_pipeline(state)

    node_hashes = [
        compute_root_hash(serialize_state(next_state)),
        compute_root_hash(serialize_state(next_state)),
        compute_root_hash(serialize_state(next_state)),
    ]

    assert node_hashes[0] == node_hashes[1] == node_hashes[2]
