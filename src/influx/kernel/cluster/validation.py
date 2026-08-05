from __future__ import annotations

from .cluster_types import ClusterLifecycle, ClusterType


def _check(name: str, passed: bool, details: str) -> dict:
    return {"check": name, "passed": passed, "details": details}


def validate_cluster_emergence_report(report: dict) -> dict:
    checks: list[dict] = []

    windows = report.get("windows", [])
    event_count = int(report.get("event_count", -1))
    window_count = int(report.get("window_count", -1))

    checks.append(_check("simulation_valid_flag", bool(report.get("simulation_valid", False)), f"simulation_valid={report.get('simulation_valid', False)}"))
    checks.append(_check("window_count_matches", window_count == len(windows), f"window_count={window_count} actual={len(windows)}"))

    computed_event_count = sum(int(window.get("event_count", 0)) for window in windows if isinstance(window, dict))
    checks.append(_check("event_count_matches", event_count == computed_event_count, f"report={event_count} computed={computed_event_count}"))

    expected_types = {item.value for item in ClusterType}
    expected_lifecycle = {item.value for item in ClusterLifecycle}

    for index, window in enumerate(windows):
        if not isinstance(window, dict):
            checks.append(_check(f"window_{index}_shape", False, "window is not an object"))
            continue

        clusters = window.get("clusters", [])
        checks.append(_check(f"window_{index}_clusters_array", isinstance(clusters, list), f"clusters_type={type(clusters).__name__}"))

        if not isinstance(clusters, list):
            continue

        ids = [cluster.get("cluster_id", "") for cluster in clusters if isinstance(cluster, dict)]
        checks.append(_check(f"window_{index}_unique_cluster_ids", len(ids) == len(set(ids)), f"cluster_ids={len(ids)} unique={len(set(ids))}"))

        for cidx, cluster in enumerate(clusters):
            if not isinstance(cluster, dict):
                checks.append(_check(f"window_{index}_cluster_{cidx}_shape", False, "cluster is not an object"))
                continue

            cluster_type = str(cluster.get("cluster_type", ""))
            lifecycle = str(cluster.get("lifecycle", ""))
            state_score = float(cluster.get("state_score", -1.0))
            members = cluster.get("member_nodes", [])

            checks.append(_check(f"window_{index}_cluster_{cidx}_type_known", cluster_type in expected_types, f"cluster_type={cluster_type}"))
            checks.append(_check(f"window_{index}_cluster_{cidx}_lifecycle_known", lifecycle in expected_lifecycle, f"lifecycle={lifecycle}"))
            checks.append(_check(f"window_{index}_cluster_{cidx}_state_score_bounds", 0.0 <= state_score <= 1.0, f"state_score={state_score}"))
            checks.append(_check(f"window_{index}_cluster_{cidx}_members_non_empty", isinstance(members, list) and len(members) > 0, f"members={len(members) if isinstance(members, list) else 'invalid'}"))

    failures = [item for item in checks if not item["passed"]]
    return {
        "report_valid": len(failures) == 0,
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failures),
        "checks_failed": len(failures),
        "failed_checks": [item["check"] for item in failures],
        "checks": checks,
    }
