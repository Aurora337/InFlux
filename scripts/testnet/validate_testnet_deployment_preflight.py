#!/usr/bin/env python3
"""Deterministic preflight validation for testnet deployment inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "testnet" / "deployment_preflight_report.json"


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _iter_json_files(base: Path) -> list[Path]:
    if not base.exists():
        return []
    return sorted(path for path in base.rglob("*.json") if path.is_file())


def _check_directories(root: Path) -> tuple[bool, str, dict]:
    required = [
        root / "testnet" / "configs",
        root / "testnet" / "genesis",
        root / "testnet" / "validators",
    ]
    missing = [str(path.relative_to(root)) for path in required if not path.exists()]
    if missing:
        return False, f"Missing required directories: {', '.join(missing)}", {"missing": missing}
    return True, "Required directories present", {"missing": []}


def _check_json_parsing(root: Path) -> tuple[bool, str, dict]:
    targets = [
        root / "testnet" / "configs",
        root / "testnet" / "genesis",
        root / "testnet" / "validators",
    ]
    files: list[Path] = []
    for target in targets:
        files.extend(_iter_json_files(target))

    invalid: list[str] = []
    for path in sorted(files):
        try:
            with path.open("r", encoding="utf-8") as handle:
                json.load(handle)
        except Exception:
            invalid.append(str(path.relative_to(root)))

    if invalid:
        return False, f"Invalid JSON files: {', '.join(invalid)}", {"invalid": invalid, "checked": len(files)}
    return True, f"All JSON files parse successfully ({len(files)} checked)", {"invalid": [], "checked": len(files)}


def _validator_identity(path: Path) -> str:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            for key in ("validator_id", "peer_id", "id", "name"):
                value = payload.get(key)
                if isinstance(value, str) and value:
                    return value
    except Exception:
        pass
    return path.stem


def _check_validator_count(root: Path, min_validators: int) -> tuple[bool, str, dict]:
    validators_dir = root / "testnet" / "validators"
    validator_files = _iter_json_files(validators_dir)
    count = len(validator_files)
    valid = count >= min_validators
    msg = f"Validator configs found: {count}, minimum required: {min_validators}"
    return valid, msg, {"count": count, "minimum": min_validators}


def _check_duplicate_validator_identity(root: Path) -> tuple[bool, str, dict]:
    validators_dir = root / "testnet" / "validators"
    identities: dict[str, list[str]] = {}
    for file_path in _iter_json_files(validators_dir):
        identity = _validator_identity(file_path)
        identities.setdefault(identity, []).append(str(file_path.relative_to(root)))

    duplicates = {
        identity: paths
        for identity, paths in identities.items()
        if len(paths) > 1
    }
    if duplicates:
        return False, "Duplicate validator identities detected", {"duplicates": duplicates}
    return True, "Validator identities are unique", {"duplicates": {}}


def _check_launch_scripts(root: Path) -> tuple[bool, str, dict]:
    scripts = [
        root / "scripts" / "testnet" / "bootstrap_network.py",
        root / "scripts" / "testnet" / "launch_validator.py",
        root / "scripts" / "testnet" / "validator_lifecycle.py",
    ]

    missing: list[str] = []
    not_executable: list[str] = []
    for script in scripts:
        rel = str(script.relative_to(root))
        if not script.exists():
            missing.append(rel)
            continue
        if not os.access(script, os.X_OK):
            not_executable.append(rel)

    if missing or not_executable:
        parts = []
        if missing:
            parts.append(f"missing: {', '.join(missing)}")
        if not_executable:
            parts.append(f"not executable: {', '.join(not_executable)}")
        return False, "Launch script checks failed: " + "; ".join(parts), {
            "missing": missing,
            "not_executable": not_executable,
        }

    return True, "Required launch scripts are present and executable", {
        "missing": [],
        "not_executable": [],
    }


def _build_fingerprint(root: Path, min_validators: int) -> str:
    digest = hashlib.sha256()
    digest.update(f"min_validators={min_validators}".encode("utf-8"))

    watched_roots = [
        root / "testnet" / "configs",
        root / "testnet" / "genesis",
        root / "testnet" / "validators",
        root / "scripts" / "testnet" / "bootstrap_network.py",
        root / "scripts" / "testnet" / "launch_validator.py",
        root / "scripts" / "testnet" / "validator_lifecycle.py",
    ]

    files: list[Path] = []
    for entry in watched_roots:
        if entry.is_file():
            files.append(entry)
        elif entry.is_dir():
            files.extend(sorted(path for path in entry.rglob("*") if path.is_file()))

    for file_path in sorted(files):
        rel = str(file_path.relative_to(root))
        digest.update(rel.encode("utf-8"))
        digest.update(hashlib.sha256(file_path.read_bytes()).hexdigest().encode("utf-8"))

    return digest.hexdigest()


def run_preflight(root: Path, min_validators: int = 1) -> dict:
    checks = [
        ("required_directories", _check_directories),
        ("json_parse_valid", _check_json_parsing),
        ("validator_count_threshold", lambda p: _check_validator_count(p, min_validators)),
        ("unique_validator_identity", _check_duplicate_validator_identity),
        ("required_launch_scripts", _check_launch_scripts),
    ]

    check_results: dict[str, dict] = {}
    passed = 0

    for key, check in checks:
        valid, message, details = check(root)
        check_results[key] = {
            "valid": bool(valid),
            "message": message,
            "details": details,
        }
        if valid:
            passed += 1

    total = len(checks)
    score = round(passed / total, 2) if total else 0.0

    return {
        "preflight_valid": passed == total,
        "preflight_score": score,
        "checks_passed": passed,
        "checks_total": total,
        "input_fingerprint": _build_fingerprint(root, min_validators),
        "timestamp": _utc_timestamp(),
        "checks": check_results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate deterministic testnet deployment preflight.")
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root path.")
    parser.add_argument("--min-validators", type=int, default=1, help="Minimum validator config files required.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output path for JSON report.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()

    report = run_preflight(root=root, min_validators=args.min_validators)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0 if report["preflight_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
