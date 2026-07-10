from influx.identity.signature import (
    Signature,
    SignatureManager,
)


def test_signature_creation():

    manager = SignatureManager()

    signature = manager.sign(
        identity_id="node-1",
        message="hello",
        private_key="secret",
    )

    assert isinstance(
        signature,
        Signature,
    )

    assert (
        signature.signer_id
        == "node-1"
    )


def test_signature_verification():

    manager = SignatureManager()

    signature = manager.sign(
        identity_id="node-1",
        message="hello",
        private_key="secret",
    )

    # Current abstraction uses the same
    # deterministic key material for validation.
    assert (
        manager.verify(
            signature,
            "hello",
            "secret",
        )
        is True
    )


def test_invalid_signature_message():

    manager = SignatureManager()

    signature = manager.sign(
        identity_id="node-1",
        message="hello",
        private_key="secret",
    )

    assert (
        manager.verify(
            signature,
            "changed",
            "secret",
        )
        is False
    )