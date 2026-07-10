from __future__ import annotations

from typing import Protocol 

from .commit_certificate import CommitCertificate

class BlockHeader(Protocol):
    """
    Minimum block header interface.
    """

    height: int


class FinalizableBlock(Protocol):
    """
    Minimum block interface required for finalization.
    """

    header: BlockHeader

class FinalityEngine:
    """
    Coordinates block finalization.

    Converts consensus agreement into
    finalized block decisions.
    """

    def __init__(
        self,
    ) -> None:

        self.finalized_blocks: dict[int, object] = {}

        self.certificates: dict[
            str,
            CommitCertificate,
        ] = {}

    def register_certificate(
        self,
        certificate: CommitCertificate,
    ) -> None:
        """
        Store a commit certificate.
        """

        self.certificates[
            certificate.block_hash
        ] = certificate

    def verify_certificate(
        self,
        certificate: CommitCertificate,
    ) -> bool:
        """
        Verify certificate quorum.
        """

        return certificate.has_quorum()

    def finalize(
        self,
        block: FinalizableBlock,
        certificate: CommitCertificate,
    ) -> bool:
        """
        Finalize a block if certificate
        is valid.
        """

        if not self.verify_certificate(
            certificate
        ):
            return False

        self.finalized_blocks[
            block.header.height
        ] = block

        self.register_certificate(
            certificate
        )

        return True

    def is_finalized(
        self,
        height: int,
    ) -> bool:
        """
        Check finalized block existence.
        """

        return height in self.finalized_blocks

    def get_finalized(
        self,
        height: int,
    ) -> object | None:
        """
        Retrieve finalized block.
        """

        return self.finalized_blocks.get(
            height
        )

    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic finality snapshot.
        """

        return {
            "finalized_blocks":
                list(
                    self.finalized_blocks.keys()
                ),

            "certificates":
                list(
                    self.certificates.keys()
                ),
        }