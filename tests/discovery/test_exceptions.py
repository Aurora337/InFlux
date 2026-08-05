from influx.discovery.exceptions import (
    DiscoveryError,
    InvalidPeerError,
    PeerRegistrationError,
    PeerNotFoundError,
)


def test_exception_hierarchy():

    assert issubclass(
        InvalidPeerError,
        DiscoveryError,
    )

    assert issubclass(
        PeerRegistrationError,
        DiscoveryError,
    )

    assert issubclass(
        PeerNotFoundError,
        DiscoveryError,
    )