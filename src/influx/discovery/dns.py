from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DNSSeed:
    """
    Represents a DNS discovery seed.
    """

    hostname: str

    port: int


class DNSDiscovery:
    """
    DNS-based discovery abstraction.

    Provides a deterministic interface for
    resolving network seed information.
    """

    def __init__(
        self,
    ) -> None:

        self._seeds: list[
            DNSSeed
        ] = []

    def add_seed(
        self,
        seed: DNSSeed,
    ) -> None:
        """
        Add DNS seed.
        """

        self._seeds.append(
            seed
        )

    def seeds(
        self,
    ) -> list[DNSSeed]:
        """
        Return registered seeds.
        """

        return list(
            self._seeds
        )

    def resolve(
        self,
    ) -> list[str]:
        """
        Resolve configured seed hosts.

        This abstraction intentionally avoids
        direct network calls. Resolution can
        later be connected to production DNS.
        """

        return [
            seed.hostname
            for seed in self._seeds
        ]