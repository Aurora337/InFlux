"""
InFlux Deterministic Event System.

Provides the universal communication layer for the protocol.
Every subsystem emits deterministic events that flow through
the event bus to the economic executor, ledger, and consensus.

Flow:
    Subsystem → Event → EventBus → EventQueue → EventDispatcher → Handlers

Key components:
    - Event: Deterministic event definition with hashing
    - EventType: Canonical event types for the protocol
    - EventBus: Publish/subscribe bus with ordered delivery
    - EventQueue: Ordered, replayable event queue
    - EventDispatcher: Routes events to registered handlers
    - EventRegistry: Event type registration and validation
    - EventFilter: Composable event filtering
    - EventSnapshot: Deterministic event state snapshots
    - EventHash: Event content hashing utilities
"""

from influx.events.event import (
    Event,
    EventType,
    create_event,
)
from influx.events.event_bus import EventBus
from influx.events.event_queue import EventQueue
from influx.events.event_dispatcher import (
    EventDispatcher,
    DispatchReceipt,
)
from influx.events.event_registry import (
    EventRegistry,
    EventRegistration,
)
from influx.events.event_filter import (
    EventFilter,
    filter_by_type,
    filter_by_source,
    filter_by_block_range,
    filter_by_time_range,
    filter_by_payload,
)
from influx.events.event_snapshot import (
    EventSnapshot,
    EventSnapshotManager,
)
from influx.events.event_hash import (
    compute_content_hash,
    verify_event_chain,
    verify_event_chain_from_root,
    compute_chain_root,
    compute_chain_tip,
)

__all__ = [
    "Event",
    "EventType",
    "create_event",
    "EventBus",
    "EventQueue",
    "EventDispatcher",
    "DispatchReceipt",
    "EventRegistry",
    "EventRegistration",
    "EventFilter",
    "filter_by_type",
    "filter_by_source",
    "filter_by_block_range",
    "filter_by_time_range",
    "filter_by_payload",
    "EventSnapshot",
    "EventSnapshotManager",
    "compute_content_hash",
    "verify_event_chain",
    "verify_event_chain_from_root",
    "compute_chain_root",
    "compute_chain_tip",
]
