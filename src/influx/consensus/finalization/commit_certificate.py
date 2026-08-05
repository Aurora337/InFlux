from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class CommitCertificate:
    """
    Represents deterministic validator agreement
    for a finalized block.
    """

    block_hash: str

    height: int

    validators: list[str] = field(
        default_factory=list
    )

    threshold: int = 0

    def add_validator(
        self,
        validator_id: str,
    ) -> None:
        """
        Add validator approval.
        """

        if validator_id not in self.validators:
            self.validators.append(
                validator_id
            )

    def has_quorum(
        self,
    ) -> bool:
        """
        Check whether enough validators
        approved the block.
        """

        return (
            len(self.validators)
            >= self.threshold
        )

    def snapshot(
        self,
    ) -> dict:
        """
        Deterministic certificate snapshot.
        """

        return {
            "block_hash":
                self.block_hash,

            "height":
                self.height,

            "validators":
                list(self.validators),

            "threshold":
                self.threshold,

            "quorum":
                self.has_quorum(),
        }