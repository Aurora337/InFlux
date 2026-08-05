from influx.network.consensus.consensus import Consensus
from influx.network.consensus.consensus_state import (
    ConsensusState,
)


def test_defaults():
    consensus = Consensus()

    assert consensus.state is ConsensusState.IDLE


def test_propose():
    consensus = Consensus()

    consensus.propose()

    assert consensus.state is ConsensusState.PROPOSING


def test_vote():
    consensus = Consensus()

    consensus.begin_vote()

    assert consensus.state is ConsensusState.VOTING


def test_commit():
    consensus = Consensus()

    consensus.commit()

    assert consensus.result.accepted
    assert consensus.state is ConsensusState.COMMITTED


def test_fail():
    consensus = Consensus()

    consensus.fail()

    assert consensus.state is ConsensusState.FAILED