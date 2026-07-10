from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NetworkEndpoint:
    """
    Deterministic network endpoint.
    """

    host: str

    port: int