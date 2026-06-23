from influx.kernel.sync.shcm import verify_state_hash


def test_validator_consensus_mismatch_majority_passes():
    state_hash = "abc123"

    peer_hashes = [
        "abc123",
        "abc123",
        "zzz999",
    ]

    assert verify_state_hash(state_hash, peer_hashes)


def test_validator_consensus_mismatch_majority_fails():
    state_hash = "abc123"

    peer_hashes = [
        "abc123",
        "zzz999",
        "zzz999",
    ]

    assert not verify_state_hash(state_hash, peer_hashes)
