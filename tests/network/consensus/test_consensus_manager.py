from influx.network.consensus.consensus import Consensus
from influx.network.consensus.consensus_manager import (
    ConsensusManager,
)
from influx.network.consensus.consensus_state import (
    ConsensusState,
)


def test_begin():
    manager = ConsensusManager()

    consensus = Consensus()

    assert manager.begin(
        consensus
    )

    assert (
        consensus.state
        is ConsensusState.PROPOSING
    )


def test_commit():
    manager = ConsensusManager()

    consensus = Consensus()

    manager.begin(
        consensus
    )

    manager.commit(
        consensus
    )

    assert (
        consensus.state
        is ConsensusState.COMMITTED
    )

    assert (
        manager.metrics.rounds_committed
        == 1
    )