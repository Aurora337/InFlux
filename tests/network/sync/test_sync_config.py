from influx.network.sync.sync_config import SyncConfig


def test_defaults():

    config = SyncConfig()

    assert config.max_peers == 32


def test_validate():

    SyncConfig().validate()