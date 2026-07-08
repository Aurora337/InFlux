from influx.kernel.sync.shcm import verify_state_hash


def test_consensus_failure():

    state_hash = "abc123"

    peers = [
        "abc123",
        "xyz999",
        "xyz999",
        "abc123"
    ]

    assert not verify_state_hash(
        state_hash,
        peers
    )
