from __future__ import annotations

from .commit_certificate import (
    CommitCertificate,
)


class Finalizer:
    """
    Creates finalized block decisions
    from consensus agreement.
    """

    def __init__(
        self,
        quorum_threshold: int,
    ) -> None:

        self.quorum_threshold = (
            quorum_threshold
        )

    def create_certificate(
        self,
        block,
        validators: list[str],
    ) -> CommitCertificate:
        """
        Create deterministic commit certificate.
        """

        certificate = CommitCertificate(
            block_hash=block.header.block_hash,
            height=block.header.height,
            threshold=self.quorum_threshold,
        )

        for validator in validators:
            certificate.add_validator(
                validator
            )

        return certificate

    def finalize(
        self,
        block,
        validators: list[str],
    ) -> bool:
        """
        Determine if block reached finality.
        """

        certificate = (
            self.create_certificate(
                block,
                validators,
            )
        )

        return certificate.has_quorum()