"""
Cross-contract call context and propagation.

Provides deterministic call context tracking,
reentrancy guards, and call depth management
for inter-contract communication.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .exceptions import ContractExecutionError


@dataclass(frozen=True, slots=True)
class CallContext:
    """
    Deterministic cross-contract call context.

    Tracks the call chain for reentrancy
    detection and depth management.
    """

    caller: str
    contract_id: str
    function: str
    value: int = 0
    gas_limit: int = 0


@dataclass(slots=True)
class CallStack:
    """
    Deterministic call stack for reentrancy guard.

    Maintains a bounded call depth and
    tracks the full call chain for audit.
    """

    max_depth: int = 10
    _stack: list[CallContext] = field(default_factory=list)

    def push(
        self,
        context: CallContext,
    ) -> None:
        """
        Push a call context onto the stack.
        """

        if len(self._stack) >= self.max_depth:
            raise ContractExecutionError(
                f"Call depth exceeded maximum of {self.max_depth}."
            )

        self._stack.append(context)

    def pop(self) -> CallContext:
        """
        Pop the top call context from the stack.
        """

        if not self._stack:
            raise ContractExecutionError(
                "Call stack is empty."
            )

        return self._stack.pop()

    def peek(self) -> CallContext | None:
        """
        Peek at the top call context without removing.
        """

        if not self._stack:
            return None

        return self._stack[-1]

    def depth(self) -> int:
        """
        Return current call depth.
        """

        return len(self._stack)

    def is_empty(self) -> bool:
        """
        Check if the call stack is empty.
        """

        return len(self._stack) == 0

    def is_reentrant(
        self,
        contract_id: str,
        function: str,
    ) -> bool:
        """
        Check if a contract/function is already in the call chain.

        Returns True if reentrant call detected.
        """

        for ctx in self._stack:
            if (
                ctx.contract_id == contract_id
                and ctx.function == function
            ):
                return True

        return False

    def call_chain(self) -> list[dict[str, Any]]:
        """
        Return the full call chain for audit/logging.
        """

        return [
            {
                "caller": ctx.caller,
                "contract_id": ctx.contract_id,
                "function": ctx.function,
                "value": ctx.value,
            }
            for ctx in self._stack
        ]

    def reset(self) -> None:
        """
        Reset the call stack.
        """

        self._stack.clear()
