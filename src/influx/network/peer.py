from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Peer:
    """
    Represents a known peer on the InFlux network.
    """

    node_id: str

    address: str

    port: int

    active: bool = True