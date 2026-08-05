from influx.consensus.finalization.commit_certificate import (
    CommitCertificate,
)


def create_certificate():

    return CommitCertificate(
        block_hash="block-1",
        height=1,
        threshold=2,
    )


def test_certificate_creation():

    certificate = create_certificate()

    assert (
        certificate.block_hash
        == "block-1"
    )

    assert (
        certificate.height
        == 1
    )


def test_add_validator():

    certificate = create_certificate()

    certificate.add_validator(
        "validator-a"
    )

    assert (
        "validator-a"
        in certificate.validators
    )


def test_duplicate_validator():

    certificate = create_certificate()

    certificate.add_validator(
        "validator-a"
    )

    certificate.add_validator(
        "validator-a"
    )

    assert (
        len(certificate.validators)
        == 1
    )


def test_quorum_failure():

    certificate = create_certificate()

    certificate.add_validator(
        "validator-a"
    )

    assert not certificate.has_quorum()


def test_quorum_success():

    certificate = create_certificate()

    certificate.add_validator(
        "validator-a"
    )

    certificate.add_validator(
        "validator-b"
    )

    assert certificate.has_quorum()


def test_snapshot():

    certificate = create_certificate()

    snapshot = certificate.snapshot()

    assert (
        snapshot["block_hash"]
        == "block-1"
    )

    assert (
        "quorum"
        in snapshot
    )