from __future__ import annotations

from dataclasses import dataclass, field


VALID_STATES = (
    "registered",
    "active",
    "suspended",
    "retired",
)


@dataclass(slots=True)
class ContractLifecycle:
    """
    Deterministic contract lifecycle manager.
    """

    _states: dict[str, str] = field(default_factory=dict)

    def register(
        self,
        contract_id: str,
    ) -> None:
        self._states[contract_id] = "registered"

    def activate(
        self,
        contract_id: str,
    ) -> None:
        self._require_state(
            contract_id,
            {"registered", "suspended"},
        )
        self._states[contract_id] = "active"

    def suspend(
        self,
        contract_id: str,
    ) -> None:
        self._require_state(
            contract_id,
            {"active"},
        )
        self._states[contract_id] = "suspended"

    def retire(
        self,
        contract_id: str,
    ) -> None:
        self._require_state(
            contract_id,
            {"registered", "active", "suspended"},
        )
        self._states[contract_id] = "retired"

    def state(
        self,
        contract_id: str,
    ) -> str:
        return self._states[contract_id]

    def exists(
        self,
        contract_id: str,
    ) -> bool:
        return contract_id in self._states

    def count(self) -> int:
        return len(self._states)

    def snapshot(self) -> dict[str, str]:
        """
        Return a deterministic snapshot of lifecycle state.
        """
        return {
            key: self._states[key]
            for key in sorted(self._states)
        }

    def _require_state(
        self,
        contract_id: str,
        allowed: set[str],
    ) -> None:
        if contract_id not in self._states:
            raise ValueError(
                f"Unknown contract '{contract_id}'."
            )

        current = self._states[contract_id]

        if current not in allowed:
            raise ValueError(
                f"Cannot transition from '{current}'."
            )