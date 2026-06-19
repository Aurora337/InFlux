from kernel.sync.shcm import verify_state_hash


def test_validator_consensus_agreement():
    state_hash = "44b22f67d3386157f83140206ec08f30df5108ac3e074a1ab9ec520a1c66794b"

    peer_hashes = [
        state_hash,
        state_hash,
        state_hash,
    ]

    assert verify_state_hash(state_hash, peer_hashes)
