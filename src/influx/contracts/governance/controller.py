from __future__ import annotations

from dataclasses import dataclass, field

from .authority import GovernanceAuthority
from .policy import GovernancePolicy
from .role import GovernanceRole


@dataclass(slots=True)
class GovernanceController:
    """
    Deterministic governance controller.
    """

    authority: GovernanceAuthority = field(
        default_factory=GovernanceAuthority
    )

    def authorize(
        self,
        policy: GovernancePolicy,
        role: GovernanceRole,
        action: str,
    ) -> bool:
        """
        Evaluate whether an action is authorized.
        """

        return self.authority.authorize(
            policy,
            role,
            action,
        )