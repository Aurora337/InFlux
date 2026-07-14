from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class GovernanceRole:
    """
    Immutable governance role assignment.
    """

    role_id: str
    principal: str
    role: str

    def to_dict(self) -> dict[str, Any]:
        """
        Export deterministic representation.
        """
        return {
            "role_id": self.role_id,
            "principal": self.principal,
            "role": self.role,
        }

    def has_role(
        self,
        role: str,
    ) -> bool:
        """
        Determine whether this assignment matches the requested role.
        """
        return self.role == role