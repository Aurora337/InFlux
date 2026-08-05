from __future__ import annotations

from enum import Enum


class MessageType(str, Enum):
    """
    Canonical message types exchanged across the InFlux network.

    Every network subsystem communicates using one of these message
    classifications. Additional message types should be appended
    rather than modifying existing values to preserve protocol
    compatibility.
    """

    # ------------------------------------------------------------------
    # Connection Lifecycle
    # ------------------------------------------------------------------

    HANDSHAKE = "HANDSHAKE"

    HANDSHAKE_ACK = "HANDSHAKE_ACK"

    HEARTBEAT = "HEARTBEAT"

    DISCONNECT = "DISCONNECT"

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------

    ROUTE_DISCOVERY = "ROUTE_DISCOVERY"

    ROUTE_UPDATE = "ROUTE_UPDATE"

    ROUTE_REMOVE = "ROUTE_REMOVE"

    # ------------------------------------------------------------------
    # State Synchronization
    # ------------------------------------------------------------------

    STATE_REQUEST = "STATE_REQUEST"

    STATE_RESPONSE = "STATE_RESPONSE"

    STATE_SNAPSHOT = "STATE_SNAPSHOT"

    # ------------------------------------------------------------------
    # Consensus
    # ------------------------------------------------------------------

    PROPOSAL = "PROPOSAL"

    VOTE = "VOTE"

    FINALIZATION = "FINALIZATION"

    # ------------------------------------------------------------------
    # Ledger
    # ------------------------------------------------------------------

    TRANSACTION = "TRANSACTION"

    BLOCK = "BLOCK"

    BLOCK_REQUEST = "BLOCK_REQUEST"

    BLOCK_RESPONSE = "BLOCK_RESPONSE"

    # ------------------------------------------------------------------
    # Economic Engine
    # ------------------------------------------------------------------

    ECONOMIC_EVENT = "ECONOMIC_EVENT"

    TOKEN_REPRODUCTION = "TOKEN_REPRODUCTION"

    # ------------------------------------------------------------------
    # Observability
    # ------------------------------------------------------------------

    METRICS = "METRICS"

    AUDIT = "AUDIT"

    LOG = "LOG"

    # ------------------------------------------------------------------
    # Generic
    # ------------------------------------------------------------------

    CUSTOM = "CUSTOM"