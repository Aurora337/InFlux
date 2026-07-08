from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI(title="InFlux Replay Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# SIMPLE HTML VISUALIZER
# -----------------------------

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>InFlux Replay Dashboard</title>
    <style>
        body { font-family: monospace; background: #0b0f14; color: #00ffcc; }
        .node { padding: 8px; margin: 4px; border: 1px solid #00ffcc; }
        .title { font-size: 18px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="title">InFlux Deterministic Replay Viewer</div>
    <div id="output"></div>

    <script>
        const output = document.getElementById("output");

        async function load() {
            const res = await fetch("/state");
            const data = await res.json();

            output.innerHTML = "";

            data.nodes.forEach((n, i) => {
                const div = document.createElement("div");
                div.className = "node";
                div.innerHTML = `
                    Node ${i}<br/>
                    Hash: ${n.hash}<br/>
                    Valid: ${n.valid}
                `;
                output.appendChild(div);
            });
        }

        setInterval(load, 1000);
        load();
    </script>
</body>
</html>
"""

# -----------------------------
# RUNTIME STATE STORE
# -----------------------------

RUNTIME_STATE: dict[str, Any] = {
    "nodes": []
}

# -----------------------------
# DASHBOARD ROUTES
# -----------------------------

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_PAGE


@app.get("/state")
def get_state():
    return RUNTIME_STATE


@app.post("/update")
def update_state(payload: dict):
    """
    Receives replay/cluster/faultnet results
    """
    RUNTIME_STATE["nodes"] = payload.get("nodes", [])
    return {"status": "updated"}