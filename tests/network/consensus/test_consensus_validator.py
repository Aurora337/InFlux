from influx.network.consensus.consensus import Consensus
from influx.network.consensus.consensus_validator import (
    ConsensusValidator,
)


def test_validate():
    validator = ConsensusValidator()

    assert validator.validate(
        Consensus()
    )