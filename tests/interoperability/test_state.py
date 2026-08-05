from influx.interoperability.cross_network_state import (
    CrossNetworkState,
    StateVerifier,
)


def test_state_verification_success():

    verifier = StateVerifier()

    state = CrossNetworkState(
        network_id="cluster-a",
        state_root="abc123",
        height=100,
    )

    assert (
        verifier.verify(
            state,
            expected_height=100,
        )
        is True
    )


def test_state_verification_failure():

    verifier = StateVerifier()

    state = CrossNetworkState(
        network_id="cluster-a",
        state_root="abc123",
        height=100,
    )

    assert (
        verifier.verify(
            state,
            expected_height=101,
        )
        is False
    )


def test_state_fields():

    state = CrossNetworkState(
        network_id="cluster-b",
        state_root="deadbeef",
        height=42,
    )

    assert state.network_id == "cluster-b"
    assert state.state_root == "deadbeef"
    assert state.height == 42