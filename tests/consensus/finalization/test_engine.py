from influx.consensus.finalization.finality_engine import (
    FinalityEngine,
)

from influx.consensus.finalization.commit_certificate import (
    CommitCertificate,
)


class Header:

    block_hash = "block-1"

    height = 1


class Block:

    header = Header()



def create_certificate():

    certificate = CommitCertificate(
        block_hash="block-1",
        height=1,
        threshold=2,
    )

    certificate.add_validator(
        "validator-a"
    )

    certificate.add_validator(
        "validator-b"
    )

    return certificate


def test_register_certificate():

    engine = FinalityEngine()

    certificate = create_certificate()

    engine.register_certificate(
        certificate
    )

    assert (
        "block-1"
        in engine.certificates
    )


def test_verify_certificate():

    engine = FinalityEngine()

    certificate = create_certificate()

    assert engine.verify_certificate(
        certificate
    )


def test_finalize_success():

    engine = FinalityEngine()

    result = engine.finalize(
        Block(),
        create_certificate(),
    )

    assert result is True

    assert engine.is_finalized(
        1
    )


def test_finalize_failure():

    engine = FinalityEngine()

    certificate = CommitCertificate(
        block_hash="block-1",
        height=1,
        threshold=3,
    )

    certificate.add_validator(
        "validator-a"
    )

    result = engine.finalize(
        Block(),
        certificate,
    )

    assert result is False


def test_get_finalized():

    engine = FinalityEngine()

    engine.finalize(
        Block(),
        create_certificate(),
    )

    block = engine.get_finalized(
        1
    )

    assert block is not None


def test_snapshot():

    engine = FinalityEngine()

    snapshot = engine.snapshot()

    assert (
        "finalized_blocks"
        in snapshot
    )

    assert (
        "certificates"
        in snapshot
    )