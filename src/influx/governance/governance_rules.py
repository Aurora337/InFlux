from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class GovernanceRules:
    """
    Defines governance approval requirements.
    """

    minimum_votes: int = 1

    require_active_proposal: bool = True


class GovernanceRuleEngine:
    """
    Evaluates governance requirements.
    """

    def __init__(
        self,
        rules: GovernanceRules | None = None,
    ) -> None:

        self.rules = (
            rules
            if rules is not None
            else GovernanceRules()
        )

    def valid_proposal(
        self,
        active: bool,
    ) -> bool:
        """
        Validate proposal state.
        """

        if self.rules.require_active_proposal:
            return active

        return True

    def valid_votes(
        self,
        votes: int,
    ) -> bool:
        """
        Validate vote count.
        """

        return (
            votes
            >= self.rules.minimum_votes
        )