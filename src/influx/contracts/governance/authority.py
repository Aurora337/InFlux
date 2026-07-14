from __future__ import annotations

from dataclasses import dataclass

from .policy import GovernancePolicy
from .role import GovernanceRole


@dataclass(slots=True)
class GovernanceAuthority:
    """
    Deterministic governance authority evaluator.
    """

    def authorize(
        self,
        policy: GovernancePolicy,
        role: GovernanceRole,
        action: str,
    ) -> bool:
        """
        Determine whether an action is authorized.
        """

        if not policy.matches(action):
            return False

        return role.has_role(
            policy.required_role,
        )