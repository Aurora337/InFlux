#!/usr/bin/env python3
"""
analyze_logs.py

Scan logs/ for ERROR / WARNING occurrences and produce a summary.
"""
import json
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict

LOG_DIR = Path("logs")

def analyze_log_file(path: Path):
    counts = Counter()
    levels = defaultdict(int)
    error_re = re.compile(r"\b(ERROR|WARN|WARNING|CRITICAL)\b", re.IGNORECASE)
    total_lines = 0
    with path.open("r", errors="replace") as fh:
        for line in fh:
            total_lines += 1
            m = error_re.search(line)
            if m:
                lvl = m.group(1).upper()
                levels[lvl] += 1
    return {"file": str(path), "counts": dict(levels), "total_lines": total_lines}

def main():
    if not LOG_DIR.exists():
        print(f"No logs/ directory found at {LOG_DIR.resolve()}", file=sys.stderr)
        sys.exit(2)

    summary = {"files": [], "totals": Counter()}
    for p in sorted(LOG_DIR.glob("**/*")):
        if p.is_file():
            res = analyze_log_file(p)
            summary["files"].append(res)
            for k, v in res["counts"].items():
                summary["totals"][k] += v

    out = {
        "summary": {
            "files": summary["files"],
            "totals": dict(summary["totals"])
        }
    }
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()