#!/usr/bin/env python3
"""
Audit Regression Detection - v1.1.5 Slice 1

Detects score regressions from validated audit baselines across the Sync Ops
Audit ladder. The report is deterministic:
- stable key ordering
- UTF-8 encoded JSON
- no timestamps
- no environment-dependent values
"""

import json
import sys
from pathlib import Path


REPORT_SPECS = {
    "integrity": {
        "path": "docs/audit/release_integrity_report.json",
        "score_field": "integrity_score",
        "valid_fields": ["audit_valid"],
    },
    "health": {
        "path": "docs/audit/repository_health.json",
        "score_field": "health_score",
        "valid_fields": ["health_valid"],
    },
    "readiness": {
        "path": "docs/audit/release_readiness_report.json",
        "score_field": "readiness_score",
        "valid_fields": ["release_ready"],
    },
    "monitoring": {
        "path": "docs/audit/continuous_audit_report.json",
        "score_field": "monitoring_score",
        "valid_fields": ["monitoring_valid"],
    },
    "validation": {
        "path": "docs/audit/automated_release_validation_report.json",
        "score_field": "validation_score",
        "valid_fields": ["validation_valid", "release_approved"],
    },
}


def load_json(path):
    """Load a JSON report from disk."""
    report_path = Path(path)
    if not report_path.exists():
        return None

    try:
        with report_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError):
        return None


def evaluate_spec(data, score_field, valid_fields):
    """
    Evaluate one report against expected validated baseline.

    Baseline expectation:
    - score field is numeric and equal to 1.0
    - each valid field exists, is bool, and is True
    """
    if not isinstance(data, dict):
        return True, False

    score = data.get(score_field)
    if not isinstance(score, (int, float)):
        return True, False

    baseline_valid = True
    if float(score) < 1.0:
        regression = True
    else:
        regression = False

    for valid_field in valid_fields:
        value = data.get(valid_field)
        if not isinstance(value, bool):
            return True, False
        if not value:
            regression = True

    return regression, baseline_valid


def build_regression_report():
    """Build deterministic regression detection report."""
    regressions = {
        "integrity_regression": True,
        "health_regression": True,
        "readiness_regression": True,
        "monitoring_regression": True,
        "validation_regression": True,
    }

    baseline_valid = True

    for name, spec in REPORT_SPECS.items():
        data = load_json(spec["path"])
        regression, valid = evaluate_spec(
            data,
            spec["score_field"],
            spec["valid_fields"],
        )
        regressions[f"{name}_regression"] = regression
        baseline_valid = baseline_valid and valid

    regression_count = sum(1 for value in regressions.values() if value)
    regression_score = round((len(regressions) - regression_count) / len(regressions), 2)
    regression_detected = regression_count > 0

    return {
        "regression_detected": regression_detected,
        "regression_score": regression_score,
        "integrity_regression": regressions["integrity_regression"],
        "health_regression": regressions["health_regression"],
        "readiness_regression": regressions["readiness_regression"],
        "monitoring_regression": regressions["monitoring_regression"],
        "validation_regression": regressions["validation_regression"],
        "baseline_valid": baseline_valid,
    }


def write_report(report):
    """Write deterministic JSON report."""
    report_path = Path("docs/audit/audit_regression_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with report_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")



def main():
    report = build_regression_report()
    write_report(report)

    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))

    if report["regression_detected"] or not report["baseline_valid"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
