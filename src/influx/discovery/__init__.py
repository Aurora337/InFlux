"""
InFlux Peer Discovery Layer.

Provides:

- bootstrap discovery
- peer exchange
- peer registry
- DNS seed discovery
"""

from .registry import (
    PeerRecord,
    PeerRegistry,
)

from .bootstrap import (
    BootstrapNode,
    BootstrapManager,
)

from .peer_exchange import (
    PeerExchange,
)

from .dns import (
    DNSSeed,
    DNSDiscovery,
)

from .exceptions import (
    DiscoveryError,
    InvalidPeerError,
    PeerRegistrationError,
    PeerNotFoundError,
)


__all__ = [
    "PeerRecord",
    "PeerRegistry",
    "BootstrapNode",
    "BootstrapManager",
    "PeerExchange",
    "DNSSeed",
    "DNSDiscovery",
    "DiscoveryError",
    "InvalidPeerError",
    "PeerRegistrationError",
    "PeerNotFoundError",
]