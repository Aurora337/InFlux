from __future__ import annotations

from dataclasses import dataclass, field

from .address import NetworkAddress
from .errors import PeerError


@dataclass(slots=True)
class Peer:
    """
    Deterministic network peer.
    """

    peer_id: str = ""
    address: NetworkAddress | str | None = None
    port: int = 0

    online: bool = False

    metadata: dict[str, str] = field(
        default_factory=dict
    )

    node_id: str = "" 

    def __post_init__(self) -> None:
        """
        Normalize compatibility fields.
        """

        if not self.peer_id:
            self.peer_id = self.node_id

        if not self.node_id:
            self.node_id = self.peer_id

        if isinstance(self.address, str):

            if self.port is None:
                raise PeerError(
                    "missing port"
                )

            self.address = NetworkAddress(
                self.address,
                self.port,
            )

    @property
    def active(self) -> bool:
        """
        Compatibility state for connection validation.

        A configured peer is considered active
        for connection admission.
        """

        return bool(
            self.peer_id
            and self.address
        )
        
    @active.setter
    def active(
        self,
        value: bool,
    ) -> None:
        """
        Update peer activity state.
        """

        self.online = value

    def connect(self) -> None:
        """
        Activate peer.
        """

        if not self.node_id:
            raise PeerError(
                "missing node id"
            )

        if self.address is None:
            raise PeerError(
                "missing address"
            )

        if isinstance(self.address, str):
            self.address = NetworkAddress(
                self.address,
                self.port,
           )

        assert isinstance(self.address, NetworkAddress)

        self.address.validate()

        self.online = True

    def disconnect(self) -> None:
        """
        Disconnect peer.
        """

        self.online = False

    def is_online(self) -> bool:
        return self.online