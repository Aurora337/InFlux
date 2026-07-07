import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from influx.testnet.bootstrap import bootstrap_from_genesis


def _write_genesis(path: Path) -> None:
    payload = {
        "network_id": "ifx-testnet-001",
        "reserve": 1000000.0,
        "circulation": 250000.0,
        "clusters": [{"cluster_id": "cluster-1"}],
        "validators": [
            {"node_id": "node-vn-1", "role": "VN"},
            {"node_id": "node-sn-1", "role": "SN"},
            {"node_id": "node-ren-1", "role": "REN"},
            {"node_id": "node-ln-1", "role": "LN"},
            {"node_id": "node-an-1", "role": "AN"},
            {"node_id": "node-ptn-1", "role": "PTN"},
            {"node_id": "node-vn-2", "role": "VN"},
        ],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def test_bootstrap_output_contract(tmp_path: Path) -> None:
    genesis_path = tmp_path / "genesis.json"
    _write_genesis(genesis_path)

    report = bootstrap_from_genesis(genesis_path)

    assert report["network_id"] == "ifx-testnet-001"
    assert isinstance(report["genesis_hash"], str)
    assert len(report["genesis_hash"]) == 64
    assert report["validator_count"] == 7
    assert report["cluster_count"] == 1


def test_bootstrap_deterministic(tmp_path: Path) -> None:
    genesis_path = tmp_path / "genesis.json"
    _write_genesis(genesis_path)

    first = bootstrap_from_genesis(genesis_path)
    second = bootstrap_from_genesis(genesis_path)

    assert first == second
