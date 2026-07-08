import argparse
import json
from typing import Any, Dict

import requests

from influx.runtime.node import InFluxNode
from influx.config.settings import InFluxConfig
from influx.simulation.run_cluster import SimulatedCluster
from influx.simulation.test_fault_network import FaultTestNetwork

import influx.observability.replay


# -----------------------------
# CONFIG BUILDER
# -----------------------------

def build_config() -> InFluxConfig:
    return InFluxConfig()


# -----------------------------
# SINGLE NODE EXECUTION
# -----------------------------

def run_single_node(event: Dict[str, Any]) -> None:
    config = build_config()

    node = InFluxNode(config.__dict__)
    node.start()

    result = node.process_event(event)

    print(json.dumps(result, indent=2))


# -----------------------------
# CLUSTER SIMULATION
# -----------------------------

def run_cluster_simulation(node_count: int, event: Dict[str, Any]) -> None:
    config = build_config()

    cluster = SimulatedCluster(node_count=node_count, config=config)

    cluster.start_all()
    results = cluster.broadcast_event(event)

    verification = cluster.verify_determinism(results)

    cluster.stop_all()

    print(json.dumps(verification, indent=2))


# -----------------------------
# FAULTNET SIMULATION
# -----------------------------

def run_faultnet(node_count: int, event: Dict[str, Any], args) -> None:
    network = FaultTestNetwork(
        node_count=node_count,
        corruption_rate=args.corruption,
        drop_rate=args.drop,
        byzantine_rate=args.byzantine
    )

    network.setup()

    results = network.broadcast_event(event)
    verification = network.verify_determinism()

    print(json.dumps({
        "results": results,
        "verification": verification
    }, indent=2))

    # Replay engine (only if a report exists)
    if "report" in verification:
        engine = influx.observability.replay.ReplayEngine(
            verification["report"]
        )
        engine.render_divergence()
        engine.render_state_mismatches()
        engine.render_timeline()

    # Push to dashboard
    try:
        requests.post(
            "http://localhost:8001/update",
            json={
                "nodes": [
                    {
                        "hash": h,
                        "valid": verification["deterministic"]
                    }
                    for h in verification["hashes"]
                ]
            }
        )
    except Exception:
        pass


# -----------------------------
# MAIN ENTRYPOINT
# -----------------------------

def main():
    parser = argparse.ArgumentParser(description="InFlux Deterministic Runtime CLI")

    parser.add_argument("--mode", type=str, required=True,
                        choices=["node", "cluster", "faultnet"])

    parser.add_argument("--nodes", type=int, default=3)
    parser.add_argument("--event", type=str, required=True)

    parser.add_argument("--byzantine", type=float, default=0.0)
    parser.add_argument("--corruption", type=float, default=0.0)
    parser.add_argument("--drop", type=float, default=0.0)

    args = parser.parse_args()

    event = json.loads(args.event)

    if args.mode == "node":
        run_single_node(event)

    elif args.mode == "cluster":
        run_cluster_simulation(args.nodes, event)

    elif args.mode == "faultnet":
        run_faultnet(args.nodes, event, args)


if __name__ == "__main__":
    main()