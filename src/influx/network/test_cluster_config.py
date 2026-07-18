import pytest

from influx.network.cluster.cluster_config import ClusterConfig


def test_default_config() -> None:
    config = ClusterConfig()

    assert config.min_members == 1
    assert config.max_members >= config.min_members


def test_validate() -> None:
    config = ClusterConfig()

    config.validate()


def test_invalid_config() -> None:
    config = ClusterConfig(
        min_members=5,
        max_members=4,
    )

    with pytest.raises(ValueError):
        config.validate()