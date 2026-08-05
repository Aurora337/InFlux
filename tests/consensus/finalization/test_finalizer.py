from influx.consensus.finalization.finalizer import (
    Finalizer,
)


class Header:

    block_hash = "block-1"

    height = 1


class Block:

    header = Header()



def test_create_certificate():

    finalizer = Finalizer(
        quorum_threshold=2
    )

    certificate = (
        finalizer.create_certificate(
            Block(),
            [
                "validator-a",
                "validator-b",
            ],
        )
    )

    assert (
        certificate.block_hash
        == "block-1"
    )

    assert (
        len(certificate.validators)
        == 2
    )


def test_finalize_success():

    finalizer = Finalizer(
        quorum_threshold=2
    )

    result = finalizer.finalize(
        Block(),
        [
            "validator-a",
            "validator-b",
        ],
    )

    assert result is True


def test_finalize_failure():

    finalizer = Finalizer(
        quorum_threshold=3
    )

    result = finalizer.finalize(
        Block(),
        [
            "validator-a",
        ],
    )

    assert result is False