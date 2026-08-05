from influx.network.consensus.consensus_state import ConsensusState


def test_states_exist():
    assert ConsensusState.IDLE.value == "idle"
    assert ConsensusState.PROPOSING.value == "proposing"
    assert ConsensusState.VOTING.value == "voting"
    assert ConsensusState.COMMITTED.value == "committed"
    assert ConsensusState.FAILED.value == "failed"