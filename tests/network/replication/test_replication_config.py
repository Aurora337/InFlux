from influx.network.replication.replication_config import (
    ReplicationConfig,
)


def test_defaults():
    config = ReplicationConfig()

    assert config.max_replicas == 3


def test_validate():
    config = ReplicationConfig()

    config.validate()