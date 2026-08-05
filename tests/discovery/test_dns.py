from influx.discovery.dns import (
    DNSSeed,
    DNSDiscovery,
)


def test_add_dns_seed():

    discovery = DNSDiscovery()

    seed = DNSSeed(
        hostname="seed.influx.network",
        port=9000,
    )

    discovery.add_seed(
        seed
    )

    assert len(
        discovery.seeds()
    ) == 1


def test_resolve_dns_seeds():

    discovery = DNSDiscovery()

    discovery.add_seed(
        DNSSeed(
            hostname="seed.influx.network",
            port=9000,
        )
    )

    hosts = discovery.resolve()

    assert (
        hosts[0]
        == "seed.influx.network"
    )


def test_multiple_dns_seeds():

    discovery = DNSDiscovery()

    discovery.add_seed(
        DNSSeed(
            hostname="seed1.influx.network",
            port=9000,
        )
    )

    discovery.add_seed(
        DNSSeed(
            hostname="seed2.influx.network",
            port=9001,
        )
    )

    assert len(
        discovery.seeds()
    ) == 2