"""
Deterministic event content hashing for the InFlux protocol.

Provides hash verification, chain integrity checks,
and content-addressed event identification.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Sequence

from .event import Event


def compute_content_hash(payload: dict[str, Any]) -> str:
    """
    Compute a deterministic content hash for event payloads.

    Args:
        payload: Arbitrary JSON-serializable dictionary

    Returns:
        Hex-encoded SHA-256 hash of the canonicalized payload
    """
    canonical = _canonicalize(payload)
    serialized = json.dumps(
        canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _canonicalize(value: Any) -> Any:
    """
    Recursively canonicalize a value for deterministic serialization.

    - Dictionaries are sorted by key
    - Floats are converted to strings to avoid precision issues
    - Enums are converted to their values
    - Lists are recursively canonicalized
    """
    if isinstance(value, dict):
        return {str(k): _canonicalize(v) for k, v in sorted(value.items())}
    elif isinstance(value, list):
        return [_canonicalize(v) for v in value]
    elif isinstance(value, float):
        return str(value)
    elif hasattr(value, "value"):
        return str(value.value)
    return value


def verify_event_chain(events: Sequence[Event]) -> bool:
    """
    Verify the integrity of a chain of events.

    Each event's previous_hash must match the hash of the preceding event.

    Args:
        events: Ordered sequence of events

    Returns:
        True if the entire chain is valid
    """
    for i in range(1, len(events)):
        previous = events[i - 1]
        current = events[i]

        if current.previous_hash != previous.hash:
            return False

        if not current.verify():
            return False

    # Verify the first event if it has no previous
    if events and events[0].previous_hash:
        return False

    return True


def verify_event_chain_from_root(
    events: Sequence[Event], root_hash: str
) -> bool:
    """
    Verify event chain integrity starting from a known root hash.

    Args:
        events: Ordered sequence of events
        root_hash: The expected hash of the first event

    Returns:
        True if the chain is valid and matches the root
    """
    if not events:
        return root_hash == ""

    if events[0].hash != root_hash:
        return False

    return verify_event_chain(events)


def compute_chain_root(events: Sequence[Event]) -> str:
    """
    Compute the root hash of an event chain.

    The root hash is the hash of the first event (or empty string if empty).

    Args:
        events: Ordered sequence of events

    Returns:
        Root hash of the event chain
    """
    if not events:
        return ""
    return events[0].hash


def compute_chain_tip(events: Sequence[Event]) -> str:
    """
    Compute the tip hash of an event chain.

    The tip hash is the hash of the last event (or empty string if empty).

    Args:
        events: Ordered sequence of events

    Returns:
        Tip hash of the event chain
    """
    if not events:
        return ""
    return events[-1].hash


def hash_event_type(event_type: Any) -> str:
    """
    Compute a deterministic hash for an event type identifier.

    Args:
        event_type: The event type (string or Enum)

    Returns:
        Hex-encoded SHA-256 hash
    """
    type_str = str(event_type.value) if hasattr(event_type, "value") else str(event_type)
    return hashlib.sha256(type_str.encode("utf-8")).hexdigest()


def hash_event_fields(fields: dict[str, Any]) -> str:
    """
    Compute a deterministic hash for a set of event fields.

    Useful for content-addressed event identification.

    Args:
        fields: Dictionary of event fields

    Returns:
        Hex-encoded SHA-256 hash
    """
    return compute_content_hash(fields)
