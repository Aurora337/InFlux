from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class GovernancePolicy:
    """
    Immutable governance policy.
    """

    policy_id: str
    action: str
    required_role: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        """
        Export deterministic representation.
        """
        return {
            "policy_id": self.policy_id,
            "action": self.action,
            "required_role": self.required_role,
            "description": self.description,
        }

    def matches(
        self,
        action: str,
    ) -> bool:
        """
        Determine whether this policy governs an action.
        """
        return self.action == action