"""
Process Manager for InFlux testnet.

Launches and manages real node processes for multi-node testnet scenarios.
Uses subprocess to run actual node instances with real sockets and networking.
"""

from __future__ import annotations

import json
import logging
import os
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class NodeProcess:
    """Represents a running node process."""

    node_id: str
    process: subprocess.Popen
    port: int
    data_dir: str
    started_at: float
    pid: int = 0

    def __post_init__(self) -> None:
        self.pid = self.process.pid

    @property
    def is_running(self) -> bool:
        """Check if the process is still running."""
        return self.process.poll() is None

    @property
    def return_code(self) -> Optional[int]:
        """Get the return code if the process has exited."""
        return self.process.returncode

    def stop(self, timeout: float = 10.0) -> bool:
        """Stop the node process gracefully."""
        if not self.is_running:
            return True

        try:
            self.process.send_signal(signal.SIGTERM)
            self.process.wait(timeout=timeout)
            return True
        except subprocess.TimeoutExpired:
            logger.warning(f"Node {self.node_id} did not stop gracefully, sending SIGKILL")
            self.process.kill()
            self.process.wait()
            return False

    def snapshot(self) -> dict[str, object]:
        """Return a snapshot of the node process state."""
        return {
            "node_id": self.node_id,
            "pid": self.pid,
            "port": self.port,
            "is_running": self.is_running,
            "uptime": time.time() - self.started_at,
            "return_code": self.return_code,
        }


class ProcessManager:
    """
    Manages the lifecycle of multiple node processes.

    Launches, monitors, and stops node processes for testnet scenarios.
    Each node runs as a separate subprocess with its own port and data directory.
    """

    def __init__(self, base_port: int = 9000):
        self.base_port = base_port
        self._nodes: dict[str, NodeProcess] = {}
        self._temp_dirs: list[str] = []

    def launch_node(
        self,
        node_id: str,
        config: dict | None = None,
        wait_for_ready: bool = True,
        ready_timeout: float = 30.0,
    ) -> NodeProcess:
        """
        Launch a single node as a subprocess.

        Args:
            node_id: Unique identifier for the node
            config: Optional configuration overrides
            wait_for_ready: Whether to wait for the node to signal readiness
            ready_timeout: Maximum time to wait for readiness

        Returns:
            NodeProcess instance representing the running node
        """
        if node_id in self._nodes:
            raise ValueError(f"Node {node_id} is already running")

        port = self.base_port + len(self._nodes)
        data_dir = tempfile.mkdtemp(prefix=f"influx_node_{node_id}_")
        self._temp_dirs.append(data_dir)

        # Build command to launch the node
        cmd = [
            sys.executable,
            "-m",
            "influx.testnet.node_runner",
            "--node-id", node_id,
            "--port", str(port),
            "--data-dir", data_dir,
        ]

        if config:
            config_path = os.path.join(data_dir, "config.json")
            with open(config_path, "w") as f:
                json.dump(config, f)
            cmd.extend(["--config", config_path])

        logger.info(f"Launching node {node_id} on port {port} with data dir {data_dir}")

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        node_process = NodeProcess(
            node_id=node_id,
            process=process,
            port=port,
            data_dir=data_dir,
            started_at=time.time(),
        )

        self._nodes[node_id] = node_process

        if wait_for_ready:
            self._wait_for_ready(node_process, ready_timeout)

        return node_process

    def _wait_for_ready(self, node: NodeProcess, timeout: float) -> bool:
        """Wait for a node to signal it's ready."""
        start = time.time()
        while time.time() - start < timeout:
            if not node.is_running:
                return False
            # Check if node has written a ready signal
            ready_file = os.path.join(node.data_dir, "ready.signal")
            if os.path.exists(ready_file):
                return True
            time.sleep(0.1)
        logger.warning(f"Node {node.node_id} did not become ready within {timeout}s")
        return False

    def stop_node(self, node_id: str, timeout: float = 10.0) -> bool:
        """Stop a specific node."""
        if node_id not in self._nodes:
            return False
        node = self._nodes.pop(node_id)
        return node.stop(timeout=timeout)

    def stop_all(self, timeout: float = 10.0) -> dict[str, bool]:
        """Stop all running nodes."""
        results = {}
        for node_id in list(self._nodes.keys()):
            results[node_id] = self.stop_node(node_id, timeout)
        self._cleanup_temp_dirs()
        return results

    def _cleanup_temp_dirs(self) -> None:
        """Clean up temporary data directories."""
        for dir_path in self._temp_dirs:
            try:
                import shutil
                shutil.rmtree(dir_path, ignore_errors=True)
            except Exception:
                pass
        self._temp_dirs.clear()

    def get_node(self, node_id: str) -> Optional[NodeProcess]:
        """Get a node process by ID."""
        return self._nodes.get(node_id)

    def list_nodes(self) -> list[NodeProcess]:
        """List all running nodes."""
        return list(self._nodes.values())

    def running_count(self) -> int:
        """Return the number of running nodes."""
        return sum(1 for n in self._nodes.values() if n.is_running)

    def snapshot(self) -> dict[str, object]:
        """Return a snapshot of all node processes."""
        return {
            "total_nodes": len(self._nodes),
            "running_nodes": self.running_count(),
            "nodes": {
                nid: node.snapshot()
                for nid, node in self._nodes.items()
            },
        }
