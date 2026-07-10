class DiscoveryError(Exception):
    """
    Base discovery exception.
    """


class InvalidPeerError(DiscoveryError):
    """
    Raised when peer information is invalid.
    """


class PeerRegistrationError(DiscoveryError):
    """
    Raised when peer registration fails.
    """


class PeerNotFoundError(DiscoveryError):
    """
    Raised when a peer cannot be found.
    """