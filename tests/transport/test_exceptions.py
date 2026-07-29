from influx.network.transport.transport import Transport


def test_exception_hierarchy():
    """Test transport exception hierarchy."""

    transport = Transport(transport_id="test")
    assert transport.transport_id == "test"
