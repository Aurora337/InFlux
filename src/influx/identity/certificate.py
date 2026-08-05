from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class IdentityCertificate:
    """
    Represents an identity certificate.
    """

    identity_id: str

    public_key: str

    issuer: str

    issued_at: int

    expires_at: int

    active: bool = True

    def valid(
        self,
        timestamp: int,
    ) -> bool:

        return (
            self.active
            and self.issued_at
            <= timestamp
            <= self.expires_at
        )

    def revoke(
        self,
    ) -> None:

        self.active = False


class CertificateAuthority:
    """
    Manages identity certificates.
    """

    def issue(
        self,
        identity_id: str,
        public_key: str,
        issuer: str,
        issued_at: int,
        expires_at: int,
    ) -> IdentityCertificate:

        return IdentityCertificate(
            identity_id=identity_id,
            public_key=public_key,
            issuer=issuer,
            issued_at=issued_at,
            expires_at=expires_at,
        )

    def verify(
        self,
        certificate: IdentityCertificate,
        timestamp: int,
    ) -> bool:

        return certificate.valid(
            timestamp
        )