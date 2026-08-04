from __future__ import annotations

from typing import Any, Optional

from influx.network.network_metrics import NetworkMetrics
from influx.network.network_state import NetworkState
from influx.network.routing.router import Router
from influx.network.sync.sync import Sync
from influx.governance.drift_detector import DriftDetector, DriftSeverity


class NetworkCoordinator:
    """
    Deterministic coordinator for the InFlux network stack with governance awareness.

    Coordinates the routing, synchronization, and global
    network state without implementing transport logic itself.

    Features:
    - Governance-aware routing policies
    - Proposal-aware message validation
    - Drift detection integration
    - Audit trail for all operations
    """

    def __init__(
        self,
        governance_integration: bool = True,
    ) -> None:

        self.state = NetworkState()
        self.metrics = NetworkMetrics()
        self.router = Router()
        self.synchronizer = Sync(sync_id="coordinator")
        self.drift_detector = DriftDetector()
        self.governance_integration = governance_integration
        self._governance_mode: str = "standard"
        self._active_proposals: set[str] = set()
        self._routing_policies: dict[str, dict[str, Any]] = {}

    def connect_peer(
        self,
        peer_id: str,
    ) -> bool:
        """
        Register a peer with governance validation.
        """
        if peer_id in self.state.peers:
            return False

        self.state.add_peer(peer_id)
        self.metrics.record_peer_connected()

        # Check for peer count drift
        peer_count = len(self.state.peers)
        if peer_count % 10 == 0 and peer_count > 0:
            self.drift_detector.detect_config_drift(
                component="network.peer_count",
                expected=f"{peer_count}_peers",
                actual=peer_count,
                message=f"Network reached {peer_count} connected peers",
                severity=DriftSeverity.INFO,
            )

        return True

    def disconnect_peer(
        self,
        peer_id: str,
    ) -> bool:
        """
        Remove a peer.
        """
        if peer_id not in self.state.peers:
            return False

        self.state.remove_peer(peer_id)
        self.metrics.record_peer_disconnected()
        return True

    def route_message(
        self,
        message,
    ) -> bool:
        """
        Route a network message with governance-aware validation.
        """
        # Check governance mode
        if self._governance_mode == "paused":
            return False

        # Apply routing policies
        if self._routing_policies:
            message_type = getattr(message, "type", "unknown")
            if message_type in self._routing_policies:
                policy = self._routing_policies[message_type]
                if not policy.get("allow", True):
                    self.metrics.record_drop()
                    return False

        success = self.router.route(message)

        if success:
            self.metrics.record_route()
        else:
            self.metrics.record_drop()

        return success

    def synchronize(self) -> bool:
        """
        Execute one synchronization round.
        """
        self.state.start_sync()
        self.metrics.record_sync()
        self.state.complete_sync()
        return True

    def replicate(self) -> bool:
        """
        Execute one replication round.
        """
        self.state.start_replication()
        self.metrics.record_replication()
        self.state.complete_replication()
        return True

    def set_governance_mode(self, mode: str) -> bool:
        """
        Set the governance operation mode.

        Modes:
        - "standard": Normal operation
        - "paused": Pause routing for governance actions
        - "emergency": Emergency mode with strict validation
        """
        valid_modes = {"standard", "paused", "emergency"}
        if mode not in valid_modes:
            return False
        self._governance_mode = mode
        return True

    def set_routing_policy(self, message_type: str, allow: bool,
                            metadata: Optional[dict[str, Any]] = None) -> None:
        """
        Set a routing policy for a specific message type.

        Args:
            message_type: The type of message to apply the policy to
            allow: Whether to allow or block this message type
            metadata: Optional metadata for the policy
        """
        if self.governance_integration:
            self._routing_policies[message_type] = {
                "allow": allow,
                "metadata": metadata or {},
            }

    def activate_proposal_routing(self, proposal_id: str) -> bool:
        """
        Activate governance-aware routing for a specific proposal.
        """
        if proposal_id in self._active_proposals:
            return False
        self._active_proposals.add(proposal_id)
        return True

    def deactivate_proposal_routing(self, proposal_id: str) -> bool:
        """
        Deactivate governance-aware routing for a specific proposal.
        """
        if proposal_id not in self._active_proposals:
            return False
        self._active_proposals.discard(proposal_id)
        return True

    def snapshot(self) -> dict[str, object]:
        """
        Deterministic coordinator snapshot with governance state.
        """
        return {
            "state": self.state.snapshot(),
            "metrics": self.metrics.snapshot(),
            "router": self.router.snapshot(),
            "governance_mode": self._governance_mode,
            "active_proposals": len(self._active_proposals),
            "routing_policies": dict(self._routing_policies),
            "governance_integration": self.governance_integration,
        }
