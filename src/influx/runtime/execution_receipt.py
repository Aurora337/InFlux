"""
InFlux v5.0.1
Deterministic Execution Receipt

Every protocol stage produces an immutable execution receipt.

Receipts provide:
- deterministic replay
- state transition auditing
- execution tracing
- protocol verification
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class ExecutionReceipt:
    """
    Immutable record of a protocol execution stage.
    """

    receipt_id: str
    execution_id: str

    stage: str

    block_height: int

    success: bool

    timestamp: str

    input_state_root: str | None
    output_state_root: str | None

    events: tuple[Any, ...]

    metrics: dict[str, Any]

    error: str | None

    hash: str


    @staticmethod
    def _hash_payload(payload: dict[str, Any]) -> str:
        """
        Generate deterministic receipt hash.
        """

        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()

        return hashlib.sha256(
            encoded
        ).hexdigest()


    @classmethod
    def create(
        cls,
        stage: str,
        input_state_root: str | None = None,
        output_state_root: str | None = None,
        block_height: int = 0,
        events: list[Any] | None = None,
        metrics: dict[str, Any] | None = None,
        success: bool = True,
        error: str | None = None,
        execution_id: str = "default",
    ) -> "ExecutionReceipt":
        """
        Create deterministic execution receipt.
        """

        timestamp = datetime.now(
            timezone.utc
        ).isoformat()


        payload = {
            "execution_id": execution_id,
            "stage": stage,
            "block_height": block_height,
            "success": success,
            "input_state_root": input_state_root,
            "output_state_root": output_state_root,
            "events": events or [],
            "metrics": metrics or {},
            "error": error,
        }


        receipt_hash = cls._hash_payload(
            payload
        )


        return cls(
            receipt_id=receipt_hash[:16],
            execution_id=execution_id,
            stage=stage,
            block_height=block_height,
            success=success,
            timestamp=timestamp,
            input_state_root=input_state_root,
            output_state_root=output_state_root,
            events=tuple(events or []),
            metrics=metrics or {},
            error=error,
            hash=receipt_hash,
        )


    def serialize(self) -> dict[str, Any]:
        """
        Deterministic serialization.
        """

        return {
            "receipt_id": self.receipt_id,
            "execution_id": self.execution_id,
            "stage": self.stage,
            "block_height": self.block_height,
            "success": self.success,
            "timestamp": self.timestamp,
            "input_state_root": self.input_state_root,
            "output_state_root": self.output_state_root,
            "events": list(self.events),
            "metrics": self.metrics,
            "error": self.error,
            "hash": self.hash,
        }