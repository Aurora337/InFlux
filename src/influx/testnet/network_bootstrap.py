"""
Network Bootstrap for InFlux testnet.

Bootstraps N real nodes with real sockets and networking.
Handles peer discovery, topology formation, and initial synchronization.
"""

from __future__ import annotations

import logging
import socket
import time
from dataclasses import dataclass, field
from typing import Optional

from .process_manager import ProcessManager, NodeProcess

logger = logging.getLogger(__name__)


@dataclass
class NetworkTopology:
    """Represents the network topology of bootstrapped nodes."""

    nodes: list[NodeProcess] = field(default_factory=list)
    cluster_id: str = "testnet-cluster"
    formation_time: float = 0.0

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def all_running(self) -> bool:
        return all(n.is_running for n in self.nodes)

    def snapshot(self) -> dict[str, object]:
        return {
            "cluster_id": self.cluster_id,
            "node_count": self.node_count,
            "all_running": self.all_running,
            "formation_time": self.formation_time,
            "nodes": [n.snapshot() for n in self.nodes],
        }


class NetworkBootstrapper:
    """
    Bootstraps a network of real node processes.

    Handles:
    - Launching N nodes with unique ports
    - Establishing peer connections
    - Forming cluster topology
    - Initial state synchronization
    """

    def __init__(self, base_port: int = 9000):
        self.process_manager = ProcessManager(base_port=base_port)
        self.topology: Optional[NetworkTopology] = None

    def bootstrap(
        self,
        node_count: int,
        cluster_id: str = "testnet-cluster",
        wait_for_ready: bool = True,
        ready_timeout: float = 30.0,
    ) -> NetworkTopology:
        """
        Bootstrap a network of N nodes.

        Args:
            node_count: Number of nodes to launch
            cluster_id: Cluster identifier
            wait_for_ready: Whether to wait for all nodes to be ready
            ready_timeout: Maximum time to wait for readiness

        Returns:
            NetworkTopology with all launched nodes
        """
        logger.info(f"Bootstrapping {node_count} nodes for cluster {cluster_id}")

        nodes: list[NodeProcess] = []

        # Launch all nodes
        for i in range(node_count):
            node_id = f"node-{i + 1}"
            config = {
                "cluster_id": cluster_id,
                "node_id": node_id,
                "max_peers": node_count - 1,
            }
            node = self.process_manager.launch_node(
                node_id=node_id,
                config=config,
                wait_for_ready=wait_for_ready,
                ready_timeout=ready_timeout,
            )
            nodes.append(node)
            logger.info(f"Launched {node_id} on port {node.port}")

        # Establish peer connections (ring topology)
        self._form_ring_topology(nodes)

        # Wait for stabilization
        if wait_for_ready:
            time.sleep(2.0)

        self.topology = NetworkTopology(
            nodes=nodes,
            cluster_id=cluster_id,
            formation_time=time.time(),
        )

        logger.info(f"Network bootstrapped with {node_count} nodes")
        return self.topology

    def _form_ring_topology(self, nodes: list[NodeProcess]) -> None:
        """Form a ring topology among the nodes."""
        n = len(nodes)
        for i, node in enumerate(nodes):
            # Connect to next node in ring
            next_node = nodes[(i + 1) % n]
            self._connect_nodes(node, next_node)

    def _connect_nodes(self, node_a: NodeProcess, node_b: NodeProcess) -> bool:
        """Establish a connection between two nodes."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect(("127.0.0.1", node_b.port))
            sock.sendall(f"connect:{node_a.node_id}".encode())
            sock.close()
            logger.info(f"Connected {node_a.node_id} -> {node_b.node_id}:{node_b.port}")
            return True
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            logger.warning(f"Failed to connect {node_a.node_id} -> {node_b.node_id}: {e}")
            return False

    def form_full_mesh(self, nodes: list[NodeProcess] | None = None) -> None:
        """Form a full mesh topology among all nodes."""
        targets = nodes or (self.topology.nodes if self.topology else [])
        for i, node_a in enumerate(targets):
            for node_b in targets[i + 1:]:
                self._connect_nodes(node_a, node_b)
                self._connect_nodes(node_b, node_a)

    def form_star_topology(self, center_index: int = 0) -> None:
        """Form a star topology with a center node."""
        if not self.topology or not self.topology.nodes:
            raise ValueError("No nodes available")
        nodes = self.topology.nodes
        center = nodes[center_index]
        for node in nodes:
            if node.node_id != center.node_id:
                self._connect_nodes(center, node)
                self._connect_nodes(node, center)

    def wait_for_stability(self, timeout: float = 10.0) -> bool:
        """Wait for the network to reach a stable state."""
        if not self.topology:
            return False
        start = time.time()
        while time.time() - start < timeout:
            if self.topology.all_running:
                return True
            time.sleep(0.5)
        logger.warning("Network did not reach stable state within timeout")
        return False

    def shutdown(self) -> dict[str, bool]:
        """Shutdown all nodes and clean up."""
        results = self.process_manager.stop_all()
        self.topology = None
        return results

    def snapshot(self) -> dict[str, object]:
        """Return a snapshot of the bootstrapped network."""
        return {
            "process_manager": self.process_manager.snapshot(),
            "topology": self.topology.snapshot() if self.topology else None,
        }
