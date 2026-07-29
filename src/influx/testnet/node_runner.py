"""
Node Runner for InFlux testnet.

Runs a single node as a subprocess with real networking.
Handles node initialization, peer discovery, and lifecycle.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import signal
import socket
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class NodeRunnerConfig:
    """Configuration for a node runner instance."""

    node_id: str
    port: int
    data_dir: str
    bootstrap_peers: list[str] = field(default_factory=list)
    max_peers: int = 10
    heartbeat_interval: float = 1.0
    consensus_timeout: float = 5.0


class NodeRunner:
    """
    Runs a single InFlux node as a subprocess.

    Manages the node's lifecycle including initialization,
    peer connections, consensus participation, and graceful shutdown.
    """

    def __init__(self, config: NodeRunnerConfig):
        self.config = config
        self._running = False
        self._server_socket: Optional[socket.socket] = None
        self._peers: dict[str, tuple[str, int]] = {}
        self._start_time: float = 0.0

        # Ensure data directory exists
        os.makedirs(config.data_dir, exist_ok=True)

    def initialize(self) -> bool:
        """
        Initialize the node.

        Sets up networking, creates data directories, and prepares
        the node for operation.
        """
        logger.info(f"Initializing node {self.config.node_id} on port {self.config.port}")

        try:
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind(("0.0.0.0", self.config.port))
            self._server_socket.listen(self.config.max_peers)
            self._server_socket.settimeout(1.0)
            logger.info(f"Node {self.config.node_id} listening on port {self.config.port}")
            return True
        except OSError as e:
            logger.error(f"Failed to bind to port {self.config.port}: {e}")
            return False

    def start(self) -> bool:
        """
        Start the node's main loop.

        Begins accepting connections, processing messages,
        and participating in consensus.
        """
        if not self._server_socket:
            if not self.initialize():
                return False

        self._running = True
        self._start_time = time.time()

        # Write ready signal
        ready_file = os.path.join(self.config.data_dir, "ready.signal")
        with open(ready_file, "w") as f:
            f.write(f"ready:{self.config.node_id}")

        logger.info(f"Node {self.config.node_id} started")
        return True

    def run_loop(self) -> None:
        """
        Main node operation loop.

        Accepts connections, processes messages, and maintains
        heartbeat with peers.
        """
        if not self.start():
            logger.error(f"Node {self.config.node_id} failed to start")
            return

        try:
            while self._running:
                self._process_events()
                self._send_heartbeats()
                time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info(f"Node {self.config.node_id} received shutdown signal")
        finally:
            self.stop()

    def _process_events(self) -> None:
        """Process incoming connections and messages."""
        if not self._server_socket:
            return

        try:
            client_socket, addr = self._server_socket.accept()
            logger.info(f"Node {self.config.node_id} accepted connection from {addr}")
            client_socket.close()
        except socket.timeout:
            pass
        except OSError as e:
            if self._running:
                logger.error(f"Socket error: {e}")

    def _send_heartbeats(self) -> None:
        """Send heartbeat to all connected peers."""
        for peer_id, (host, port) in list(self._peers.items()):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2.0)
                sock.connect((host, port))
                sock.sendall(f"heartbeat:{self.config.node_id}".encode())
                sock.close()
            except (socket.timeout, ConnectionRefusedError, OSError):
                logger.warning(f"Peer {peer_id} at {host}:{port} unreachable")
                self._peers.pop(peer_id, None)

    def connect_to_peer(self, host: str, port: int) -> bool:
        """
        Connect to a peer node.

        Args:
            host: Peer hostname or IP
            port: Peer port

        Returns:
            True if connection was successful
        """
        peer_id = f"{host}:{port}"
        if peer_id in self._peers:
            return True

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect((host, port))
            sock.sendall(f"connect:{self.config.node_id}".encode())
            sock.close()
            self._peers[peer_id] = (host, port)
            logger.info(f"Connected to peer {peer_id}")
            return True
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            logger.warning(f"Failed to connect to peer {peer_id}: {e}")
            return False

    def stop(self) -> None:
        """Stop the node gracefully."""
        self._running = False

        if self._server_socket:
            try:
                self._server_socket.close()
            except OSError:
                pass
            self._server_socket = None

        # Remove ready signal
        ready_file = os.path.join(self.config.data_dir, "ready.signal")
        if os.path.exists(ready_file):
            os.remove(ready_file)

        uptime = time.time() - self._start_time
        logger.info(f"Node {self.config.node_id} stopped (uptime: {uptime:.2f}s)")

    @property
    def is_running(self) -> bool:
        """Check if the node is running."""
        return self._running

    @property
    def peer_count(self) -> int:
        """Return the number of connected peers."""
        return len(self._peers)

    @property
    def uptime(self) -> float:
        """Return the node uptime in seconds."""
        if self._start_time == 0:
            return 0.0
        return time.time() - self._start_time

    def snapshot(self) -> dict[str, object]:
        """Return a snapshot of the node's state."""
        return {
            "node_id": self.config.node_id,
            "port": self.config.port,
            "running": self._running,
            "peers": len(self._peers),
            "uptime": self.uptime,
            "data_dir": self.config.data_dir,
        }


def main() -> int:
    """Entry point for running a node as a subprocess."""
    parser = argparse.ArgumentParser(description="InFlux testnet node")
    parser.add_argument("--node-id", required=True, help="Unique node identifier")
    parser.add_argument("--port", type=int, required=True, help="Node port")
    parser.add_argument("--data-dir", required=True, help="Data directory")
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--bootstrap", nargs="*", default=[], help="Bootstrap peer addresses")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s [%(levelname)s] node={args.node_id} %(message)s",
    )

    config = NodeRunnerConfig(
        node_id=args.node_id,
        port=args.port,
        data_dir=args.data_dir,
        bootstrap_peers=list(args.bootstrap),
    )

    runner = NodeRunner(config)

    # Connect to bootstrap peers
    for peer_addr in args.bootstrap:
        if ":" in peer_addr:
            host, port_str = peer_addr.split(":")
            runner.connect_to_peer(host, int(port_str))

    # Run main loop
    runner.run_loop()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
