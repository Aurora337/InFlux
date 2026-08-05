"""
Deterministic event definition for the InFlux protocol.

Every event in the system is hashed deterministically for replay
protection, audit trails, and consensus verification.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class EventType(Enum):
    """Canonical event types for the InFlux protocol."""

    # Governance events
    PROPOSAL_CREATED = "proposal_created"
    PROPOSAL_APPROVED = "proposal_approved"
    PROPOSAL_EXECUTED = "proposal_executed"
    VOTE_CAST = "vote_cast"

    # Contract events
    CONTRACT_DEPLOYED = "contract_deployed"
    CONTRACT_EXECUTED = "contract_executed"
    CONTRACT_FUNDS_TRANSFERRED = "contract_funds_transferred"

    # Economic events
    ECONOMIC_OPERATION = "economic_operation"
    BALANCE_CHANGED = "balance_changed"
    SUPPLY_CHANGED = "supply_changed"
    RESERVE_CHANGED = "reserve_changed"
    REWARD_DISTRIBUTED = "reward_distributed"
    FEE_COLLECTED = "fee_collected"
    EMISSION_OCCURRED = "emission_occurred"

    # Treasury events
    TREASURY_DEPOSIT = "treasury_deposit"
    TREASURY_WITHDRAWAL = "treasury_withdrawal"
    TREASURY_DISPERSAL = "treasury_dispersal"

    # Network events
    VALIDATOR_REGISTERED = "validator_registered"
    VALIDATOR_REWARDED = "validator_rewarded"
    CONSENSUS_REACHED = "consensus_reached"
    BLOCK_FINALIZED = "block_finalized"

    # System events
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    EPOCH_ADVANCED = "epoch_advanced"
    SNAPSHOT_CREATED = "snapshot_created"


@dataclass(slots=True)
class Event:
    """
    A deterministic event in the InFlux protocol.

    Every event carries:
    - event_id: Unique, deterministically derived identifier
    - event_type: Canonical type from EventType enum
    - source: The subsystem that emitted the event
    - payload: The event data (must be JSON-serializable)
    - block_height: The block height at which the event occurred
    - timestamp: Unix timestamp (deterministic from block time)
    - sequence: Monotonically increasing sequence number within the block
    - previous_hash: Hash of the previous event in the sequence
    - _hash: Cached deterministic hash of this event

    Properties:
    - Events are ordered within a block by sequence number
    - Each event links to the previous via previous_hash
    - The hash covers all fields except _hash itself
    - Events are immutable after creation
    """

    event_id: str
    event_type: EventType
    source: str
    payload: dict[str, Any]
    block_height: int
    timestamp: int
    sequence: int = 0
    previous_hash: str = ""
    _hash: Optional[str] = field(default=None, repr=False)

    def compute_hash(self) -> str:
        """Compute the deterministic hash of this event."""
        canonical = {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "source": self.source,
            "payload": self._canonicalize_payload(self.payload),
            "block_height": self.block_height,
            "timestamp": self.timestamp,
            "sequence": self.sequence,
            "previous_hash": self.previous_hash,
        }
        serialized = json.dumps(
            canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @staticmethod
    def _canonicalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
        """Ensure payload is deterministically serializable."""
        result: dict[str, Any] = {}
        for key, value in sorted(payload.items()):
            if isinstance(value, dict):
                result[key] = Event._canonicalize_payload(value)
            elif isinstance(value, list):
                result[key] = [
                    Event._canonicalize_payload(v) if isinstance(v, dict) else v
                    for v in value
                ]
            elif isinstance(value, float):
                # Use string representation to avoid floating-point ambiguity
                result[key] = str(value)
            elif isinstance(value, Enum):
                result[key] = value.value
            else:
                result[key] = value
        return result

    @property
    def hash(self) -> str:
        """Return cached or computed hash."""
        if self._hash is None:
            self._hash = self.compute_hash()
        return self._hash

    def snapshot(self) -> dict[str, Any]:
        """Deterministic event snapshot for audit and replay."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "source": self.source,
            "payload": self.payload,
            "block_height": self.block_height,
            "timestamp": self.timestamp,
            "sequence": self.sequence,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
        }

    def verify(self) -> bool:
        """
        Verify the event's hash integrity.
        """

        return self._hash == self.compute_hash()

def create_event(
    event_type: EventType,
    source: str,
    payload: dict[str, Any],
    block_height: int,
    timestamp: Optional[int] = None,
    sequence: int = 0,
    previous_hash: str = "",
) -> Event:
    """
    Factory function to create a deterministic event.

    Args:
        event_type: The canonical event type
        source: The subsystem emitting the event
        payload: The event data (must be JSON-serializable)
        block_height: The block height at which the event occurred
        timestamp: Unix timestamp (defaults to current time)
        sequence: Sequence number within the block
        previous_hash: Hash of the previous event

    Returns:
        A new Event with a deterministically derived event_id
    """
    if timestamp is None:
        timestamp = int(datetime.now(timezone.utc).timestamp())

    # Derive event_id deterministically from content
    content_hash = hashlib.sha256(
        json.dumps(
            {
                "event_type": event_type.value,
                "source": source,
                "payload": Event._canonicalize_payload(payload),
                "block_height": block_height,
                "timestamp": timestamp,
                "sequence": sequence,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()[:32]

    event = Event(
        event_id=content_hash,
        event_type=event_type,
        source=source,
        payload=payload,
        block_height=block_height,
        timestamp=timestamp,
        sequence=sequence,
        previous_hash=previous_hash,
    )

    event._hash = event.compute_hash()

    return event
