from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .errors import ContextError


@dataclass(slots=True)
class ExecutionContext:
    """
    Deterministic execution environment.

    Stores runtime execution metadata,
    transaction data, and temporary state.
    """

    transaction_id: str
    caller: str
    payload: dict[str, Any] = field(default_factory=dict)
    storage: dict[str, Any] = field(default_factory=dict)
    logs: list[str] = field(default_factory=list)

    def set_value(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store deterministic runtime value.
        """

        if not key:
            raise ContextError(
                "context key cannot be empty"
            )

        self.storage[key] = value

    def get_value(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve runtime value.
        """

        return self.storage.get(
            key,
            default,
        )

    def emit_log(
        self,
        message: str,
    ) -> None:
        """
        Record deterministic execution log.
        """

        self.logs.append(message)