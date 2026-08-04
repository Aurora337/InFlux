"""
Testnet Orchestrator for InFlux.

Orchestrates multi-node testnet lifecycle including:
- Network bootstrap
- Consensus rounds
- State synchronization
- Health monitoring
- Graceful shutdown
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

from .network_bootstrap import NetworkBootstrapper, NetworkTopology

logger = logging.getLogger(__name__)


@dataclass
class TestnetResult:
    """Result of a testnet orchestration run."""

    success: bool
    node_count: int
    rounds_completed: int
    consensus_rounds: int
    sync_rounds: int
    total_time: float
    errors: list[str] = field(default_factory=list)
    topology_snapshot: Optional[dict] = None


class TestnetOrchestrator:
    __test__ = False
    """
    Orchestrates the full lifecycle of a multi-node testnet.

    Handles:
    - Bootstrapping N nodes
    - Running consensus rounds
    - Synchronizing state
    - Monitoring health
    - Collecting results
    """

    def __init__(self, base_port: int = 9000):
        self.bootstrapper = NetworkBootstrapper(base_port=base_port)
        self._start_time: float = 0.0

    def run_testnet(
        self,
        node_count: int,
        consensus_rounds: int = 5,
        sync_rounds: int = 3,
        cluster_id: str = "testnet-cluster",
    ) -> TestnetResult:
        """
        Run a complete testnet lifecycle.

        Args:
            node_count: Number of nodes to launch
            consensus_rounds: Number of consensus rounds to simulate
            sync_rounds: Number of sync rounds to simulate
            cluster_id: Cluster identifier

        Returns:
            TestnetResult with success/failure and metrics
        """
        self._start_time = time.time()
        errors: list[str] = []

        logger.info(f"Starting testnet with {node_count} nodes")

        # Phase 1: Bootstrap
        try:
            topology = self.bootstrapper.bootstrap(
                node_count=node_count,
                cluster_id=cluster_id,
                wait_for_ready=True,
                ready_timeout=30.0,
            )
            logger.info(f"Bootstrapped {topology.node_count} nodes")
        except Exception as e:
            logger.error(f"Bootstrap failed: {e}")
            return TestnetResult(
                success=False,
                node_count=0,
                rounds_completed=0,
                consensus_rounds=0,
                sync_rounds=0,
                total_time=time.time() - self._start_time,
                errors=[f"Bootstrap failed: {e}"],
            )

        # Phase 2: Consensus rounds
        consensus_completed = 0
        for round_num in range(consensus_rounds):
            try:
                logger.info(f"Consensus round {round_num + 1}/{consensus_rounds}")
                self._simulate_consensus_round(topology, round_num)
                consensus_completed += 1
            except Exception as e:
                errors.append(f"Consensus round {round_num + 1} failed: {e}")
                break

        # Phase 3: Sync rounds
        sync_completed = 0
        for round_num in range(sync_rounds):
            try:
                logger.info(f"Sync round {round_num + 1}/{sync_rounds}")
                self._simulate_sync_round(topology, round_num)
                sync_completed += 1
            except Exception as e:
                errors.append(f"Sync round {round_num + 1} failed: {e}")
                break

        # Phase 4: Health check
        all_healthy = topology.all_running
        if not all_healthy:
            errors.append("Not all nodes are healthy")

        # Phase 5: Shutdown
        try:
            self.bootstrapper.shutdown()
            logger.info("Testnet shutdown complete")
        except Exception as e:
            errors.append(f"Shutdown failed: {e}")

        total_time = time.time() - self._start_time

        return TestnetResult(
            success=all_healthy and len(errors) == 0,
            node_count=node_count,
            rounds_completed=consensus_completed + sync_completed,
            consensus_rounds=consensus_completed,
            sync_rounds=sync_completed,
            total_time=total_time,
            errors=errors,
            topology_snapshot=topology.snapshot() if topology else None,
        )

    def _simulate_consensus_round(self, topology: NetworkTopology, round_num: int) -> None:
        """Simulate a consensus round across all nodes."""
        for node in topology.nodes:
            if node.is_running:
                logger.debug(f"Node {node.node_id} participating in consensus round {round_num}")
        time.sleep(0.5)

    def _simulate_sync_round(self, topology: NetworkTopology, round_num: int) -> None:
        """Simulate a sync round across all nodes."""
        for node in topology.nodes:
            if node.is_running:
                logger.debug(f"Node {node.node_id} synchronizing round {round_num}")
        time.sleep(0.3)

    def run_single_node_test(self) -> TestnetResult:
        """Run a minimal test with a single node."""
        return self.run_testnet(node_count=1, consensus_rounds=1, sync_rounds=1)

    def run_four_node_test(self) -> TestnetResult:
        """Run a standard test with four nodes."""
        return self.run_testnet(node_count=4, consensus_rounds=3, sync_rounds=2)

    def run_ten_node_test(self) -> TestnetResult:
        """Run a larger test with ten nodes."""
        return self.run_testnet(node_count=10, consensus_rounds=5, sync_rounds=3)
