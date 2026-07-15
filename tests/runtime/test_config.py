from influx.runtime.config import RuntimeConfig


def test_default_configuration() -> None:
    config = RuntimeConfig()

    assert config.node_name == "influx-node"
    assert config.host == "127.0.0.1"
    assert config.port == 9000
    assert config.rpc_enabled is True
    assert config.rpc_port == 8080
    assert config.metrics_enabled is True


def test_custom_configuration() -> None:
    config = RuntimeConfig(
        node_name="validator-1",
        host="0.0.0.0",
        port=7000,
        rpc_enabled=False,
        rpc_port=9001,
        metrics_enabled=False,
    )

    assert config.node_name == "validator-1"
    assert config.host == "0.0.0.0"
    assert config.port == 7000
    assert config.rpc_enabled is False
    assert config.rpc_port == 9001
    assert config.metrics_enabled is False


def test_to_dict() -> None:
    config = RuntimeConfig()

    data = config.to_dict()

    assert data["node_name"] == config.node_name
    assert data["host"] == config.host
    assert data["port"] == config.port


def test_from_dict() -> None:
    config = RuntimeConfig.from_dict(
        {
            "node_name": "node-2",
            "host": "192.168.1.50",
            "port": 7001,
            "rpc_enabled": False,
            "rpc_port": 9002,
            "metrics_enabled": False,
        }
    )

    assert config.node_name == "node-2"
    assert config.host == "192.168.1.50"
    assert config.port == 7001
    assert config.rpc_enabled is False
    assert config.rpc_port == 9002
    assert config.metrics_enabled is False