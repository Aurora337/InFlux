import pytest

from influx.network.consensus.consensus_config import (
    ConsensusConfig,
)


def test_defaults():
    config = ConsensusConfig()

    assert config.quorum_size == 1


def test_validate():
    ConsensusConfig().validate()


def test_invalid():
    with pytest.raises(ValueError):
        ConsensusConfig(
            quorum_size=0
        ).validate()