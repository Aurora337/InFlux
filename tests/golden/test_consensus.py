from influx.kernel.sync.shcm import verify_state_hash


def test_consensus():

    state_hash = "abc123"

    peers = [
        "abc123",
        "abc123",
        "abc123",
        "xyz999"
    ]

    assert verify_state_hash(
        state_hash,
        peers
    )
