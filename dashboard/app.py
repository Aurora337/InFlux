"""
InFlux Live Network Console — Dashboard Backend

FastAPI application serving real-time network metrics and cluster topology.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger(__name__)

app = FastAPI(title="InFlux Network Console", version="1.5.0-rc1")


@dataclass
class NetworkMetrics:
    """Real-time network metrics."""

    cluster_topology: str = "unknown"
    validator_health: float = 0.0
    gossip_propagation: float = 0.0
    consensus_rounds: int = 0
    synchronization: float = 0.0
    state_root: str = "0x0"
    tps: float = 0.0
    latency_ms: float = 0.0
    memory_mb: float = 0.0
    transport_stats: str = "idle"
    timestamp: float = 0.0

    def snapshot(self) -> dict[str, object]:
        return {
            "cluster_topology": self.cluster_topology,
            "validator_health": self.validator_health,
            "gossip_propagation": self.gossip_propagation,
            "consensus_rounds": self.consensus_rounds,
            "synchronization": self.synchronization,
            "state_root": self.state_root,
            "tps": self.tps,
            "latency_ms": self.latency_ms,
            "memory_mb": self.memory_mb,
            "transport_stats": self.transport_stats,
            "timestamp": self.timestamp or time.time(),
        }


class MetricsCollector:
    """Collects and stores real-time network metrics."""

    def __init__(self):
        self._metrics: list[NetworkMetrics] = []
        self._current = NetworkMetrics()

    def update(self, **kwargs) -> None:
        """Update current metrics with new values."""
        for key, value in kwargs.items():
            if hasattr(self._current, key):
                setattr(self._current, key, value)
        self._current.timestamp = time.time()

    def snapshot(self) -> NetworkMetrics:
        """Take a snapshot of current metrics."""
        snapshot = NetworkMetrics(
            cluster_topology=self._current.cluster_topology,
            validator_health=self._current.validator_health,
            gossip_propagation=self._current.gossip_propagation,
            consensus_rounds=self._current.consensus_rounds,
            synchronization=self._current.synchronization,
            state_root=self._current.state_root,
            tps=self._current.tps,
            latency_ms=self._current.latency_ms,
            memory_mb=self._current.memory_mb,
            transport_stats=self._current.transport_stats,
            timestamp=time.time(),
        )
        self._metrics.append(snapshot)
        if len(self._metrics) > 1000:
            self._metrics = self._metrics[-500:]
        return snapshot

    def history(self, limit: int = 100) -> list[dict[str, object]]:
        """Return metric history."""
        return [m.snapshot() for m in self._metrics[-limit:]]


collector = MetricsCollector()


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        self._connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self._connections:
            self._connections.remove(websocket)

    async def broadcast(self, data: dict[str, object]) -> None:
        for connection in self._connections:
            try:
                await connection.send_json(data)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the main dashboard page."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>InFlux Network Console</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0a0a0f; color: #e0e0e0; }
            .header { background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 20px; border-bottom: 1px solid #2a2a4a; }
            .header h1 { font-size: 24px; color: #00d4ff; }
            .header p { font-size: 14px; color: #888; margin-top: 5px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; padding: 20px; }
            .card { background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 12px; padding: 20px; }
            .card h3 { font-size: 14px; color: #888; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; }
            .card .value { font-size: 28px; font-weight: bold; color: #00d4ff; }
            .card .value.green { color: #00ff88; }
            .card .value.yellow { color: #ffd700; }
            .card .value.red { color: #ff4444; }
            .status-bar { display: flex; gap: 10px; padding: 10px 20px; background: #111; border-top: 1px solid #2a2a4a; font-size: 12px; color: #666; }
            .status-bar .dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
            .dot.green { background: #00ff88; }
            .dot.red { background: #ff4444; }
            @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
            .live { animation: pulse 2s infinite; color: #00ff88; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>InFlux Network Console</h1>
            <p>Live Network Monitor — v1.5.0-rc1</p>
        </div>
        <div class="grid" id="metrics-grid">
            <div class="card"><h3>Cluster Topology</h3><div class="value" id="cluster-topology">—</div></div>
            <div class="card"><h3>Validator Health</h3><div class="value" id="validator-health">—</div></div>
            <div class="card"><h3>Gossip Propagation</h3><div class="value" id="gossip-propagation">—</div></div>
            <div class="card"><h3>Consensus Rounds</h3><div class="value" id="consensus-rounds">—</div></div>
            <div class="card"><h3>Synchronization</h3><div class="value" id="synchronization">—</div></div>
            <div class="card"><h3>State Root</h3><div class="value" id="state-root" style="font-size:16px;word-break:break-all;">—</div></div>
            <div class="card"><h3>TPS</h3><div class="value" id="tps">—</div></div>
            <div class="card"><h3>Latency</h3><div class="value" id="latency">—</div></div>
            <div class="card"><h3>Memory</h3><div class="value" id="memory">—</div></div>
            <div class="card"><h3>Transport</h3><div class="value" id="transport-stats">—</div></div>
        </div>
        <div class="status-bar">
            <span class="dot green" id="status-dot"></span>
            <span id="status-text">Connected</span>
            <span style="margin-left:auto;" id="last-update">—</span>
        </div>
        <script>
            const ws = new WebSocket(`ws://${window.location.host}/ws`);
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                document.getElementById('cluster-topology').textContent = data.cluster_topology || '—';
                document.getElementById('validator-health').textContent = (data.validator_health * 100).toFixed(1) + '%';
                document.getElementById('gossip-propagation').textContent = (data.gossip_propagation * 100).toFixed(1) + '%';
                document.getElementById('consensus-rounds').textContent = data.consensus_rounds || 0;
                document.getElementById('synchronization').textContent = (data.synchronization * 100).toFixed(1) + '%';
                document.getElementById('state-root').textContent = data.state_root || '—';
                document.getElementById('tps').textContent = data.tps ? data.tps.toFixed(1) : '—';
                document.getElementById('latency').textContent = data.latency_ms ? data.latency_ms.toFixed(0) + 'ms' : '—';
                document.getElementById('memory').textContent = data.memory_mb ? data.memory_mb.toFixed(0) + 'MB' : '—';
                document.getElementById('transport-stats').textContent = data.transport_stats || '—';
                document.getElementById('last-update').textContent = new Date(data.timestamp * 1000).toLocaleTimeString();
            };
            ws.onclose = function() {
                document.getElementById('status-dot').className = 'dot red';
                document.getElementById('status-text').textContent = 'Disconnected';
            };
        </script>
    </body>
    </html>
    """


@app.get("/api/metrics")
async def get_metrics():
    """Return current metrics snapshot."""
    return collector.snapshot().snapshot()


@app.get("/api/history")
async def get_history(limit: int = 100):
    """Return metric history."""
    return collector.history(limit=limit)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time metric updates."""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


def run_dashboard(host: str = "0.0.0.0", port: int = 8080) -> None:
    """Run the dashboard server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_dashboard()
