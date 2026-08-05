from influx.identity.certificate import (
    CertificateAuthority,
    IdentityCertificate,
)


def test_issue_certificate():

    authority = CertificateAuthority()

    certificate = authority.issue(
        identity_id="node-1",
        public_key="public",
        issuer="root",
        issued_at=100,
        expires_at=200,
    )

    assert isinstance(
        certificate,
        IdentityCertificate,
    )

    assert (
        certificate.identity_id
        == "node-1"
    )


def test_certificate_valid():

    authority = CertificateAuthority()

    certificate = authority.issue(
        identity_id="node-1",
        public_key="public",
        issuer="root",
        issued_at=100,
        expires_at=200,
    )

    assert (
        authority.verify(
            certificate,
            150,
        )
        is True
    )


def test_certificate_expired():

    authority = CertificateAuthority()

    certificate = authority.issue(
        identity_id="node-1",
        public_key="public",
        issuer="root",
        issued_at=100,
        expires_at=200,
    )

    assert (
        authority.verify(
            certificate,
            300,
        )
        is False
    )


def test_certificate_revocation():

    authority = CertificateAuthority()

    certificate = authority.issue(
        identity_id="node-1",
        public_key="public",
        issuer="root",
        issued_at=100,
        expires_at=200,
    )

    certificate.revoke()

    assert (
        certificate.valid(150)
        is False
    )