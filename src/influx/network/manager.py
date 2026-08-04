from __future__ import annotations

from typing import Any, Optional

from influx.network.network_coordinator import NetworkCoordinator
from influx.network.transport.transport_manager import TransportManager
from influx.network.transport.transport import Transport
from influx.network.discovery.discovery_manager import DiscoveryManager
from influx.network.consensus.consensus import Consensus
from influx.network.replication.replication import Replication
from influx.network.cluster.cluster import Cluster
from influx.network.gossip.gossip import Gossip
from influx.network.peer import Peer
from influx.network.registry import PeerRegistry
from influx.network.sync.sync import Sync
from influx.governance.governance_engine import GovernanceEngine
from influx.governance.drift_detector import DriftDetector


class NetworkManager:
    """
    High-level deterministic network manager with governance integration.

    Manages the full network stack including:
    - Peer registration and discovery
    - Transport and message routing
    - Consensus and replication
    - Cluster management and gossip
    - Governance awareness (proposals, voting, drift detection)
    """

    def __init__(
        self,
        governance_enabled: bool = True,
    ) -> None:
        self.registry = PeerRegistry()
        self.coordinator = NetworkCoordinator(
            governance_integration=governance_enabled,
        )
        self.transport = TransportManager(Transport())
        self.discovery = DiscoveryManager()
        self.consensus = Consensus()
        self.replication = Replication(
            replication_id="network",
        )
        self.cluster = Cluster(
            cluster_id="main",
        )
        self.gossip = Gossip()
        self.synchronizer = Sync(
            sync_id="network",
        )
        self.governance_enabled = governance_enabled
        self.governance_engine: Optional[GovernanceEngine] = (
            GovernanceEngine() if governance_enabled else None
        )
        self.drift_detector = DriftDetector()

    def start(self) -> bool:
        """Start all network services."""
        self.discovery.start_all()
        self.synchronizer.synchronize()
        self.gossip.start()
        if self.governance_engine:
            self.drift_detector.check_all()
        return True

    def stop(self) -> bool:
        """Stop all network services."""
        self.discovery.stop_all()
        self.synchronizer.fail()
        self.gossip.stop()
        return True

    def add_peer(self, peer: Peer) -> None:
        """Register a peer and make it available to the coordinator."""
        self.registry.register(peer)
        self.coordinator.connect_peer(peer.node_id)

        if self.governance_engine:
            self.governance_engine.advance_block()

    def remove_peer(self, node_id: str) -> None:
        """Remove a peer from both the registry and coordinator."""
        self.registry.unregister(node_id)
        self.coordinator.disconnect_peer(node_id)

    def peers(self) -> list[Peer]:
        """Return registered peers in deterministic order."""
        return self.registry.peers()

    def connect(
        self,
        peer_id: str,
    ) -> bool:
        result = self.coordinator.connect_peer(peer_id)
        if result and self.governance_engine:
            self.governance_engine.advance_block()
        return result

    def disconnect(
        self,
        peer_id: str,
    ) -> bool:
        return self.coordinator.disconnect_peer(peer_id)

    def synchronize(self) -> bool:
        """Execute a synchronization round with governance awareness."""
        result = self.coordinator.synchronize()
        if result and self.governance_engine:
            self.governance_engine.advance_block()
        return result

    def get_governance_engine(self) -> Optional[GovernanceEngine]:
        """Get the governance engine if enabled."""
        return self.governance_engine

    def enable_governance_mode(self, mode: str) -> bool:
        """
        Enable governance operation mode.

        Args:
            mode: "standard", "paused", or "emergency"

        Returns:
            True if mode was set successfully
        """
        return self.coordinator.set_governance_mode(mode)

    def set_routing_policy(self, message_type: str, allow: bool,
                           metadata: Optional[dict[str, Any]] = None) -> None:
        """Set a governance-aware routing policy."""
        self.coordinator.set_routing_policy(message_type, allow, metadata)

    def snapshot(self) -> dict:
        """Deterministic network manager snapshot with governance state."""
        snapshot = {
            "coordinator": self.coordinator.snapshot(),
            "transport": self.transport.snapshot(),
            "discovery": self.discovery.snapshot(),
            "consensus": self.consensus.snapshot(),
            "replication": self.replication.snapshot(),
            "cluster": self.cluster.snapshot(),
            "gossip": self.gossip.snapshot(),
            "governance_enabled": self.governance_enabled,
        }
        if self.governance_engine:
            snapshot["governance_engine"] = self.governance_engine.snapshot()
        if self.drift_detector:
            snapshot["drift_detector"] = self.drift_detector.snapshot()
        return snapshot
