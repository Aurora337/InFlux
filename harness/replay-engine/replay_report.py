"""Generate verification reports from replay results."""

from dataclasses import dataclass


@dataclass
class ReplayReport:
    total_epochs: int
    matched_epochs: int
    mismatched_epochs: int
    all_passed: bool
    details: list[dict]

    def to_dict(self) -> dict:
        return {
            "total_epochs": self.total_epochs,
            "matched_epochs": self.matched_epochs,
            "mismatched_epochs": self.mismatched_epochs,
            "all_passed": self.all_passed,
            "details": self.details,
        }

    def summary(self) -> str:
        if self.all_passed:
            return f"✅ REPLAY VERIFICATION PASSED: {self.matched_epochs}/{self.total_epochs} epochs matched."
        else:
            return f"❌ REPLAY VERIFICATION FAILED: {self.mismatched_epochs} mismatches out of {self.total_epochs} epochs."


class ReplayReportGenerator:
    def __init__(self):
        pass

    def generate(self, replay_results: list[dict]) -> ReplayReport:
        total = len(replay_results)
        matched = sum(1 for r in replay_results if r["match"])
        mismatched = total - matched
        all_passed = mismatched == 0

        details = [
            {
                "epoch": r["epoch"],
                "recorded_hash": r["recorded_hash"],
                "recomputed_hash": r["recomputed_hash"],
                "match": r["match"],
            }
            for r in replay_results
        ]

        return ReplayReport(
            total_epochs=total,
            matched_epochs=matched,
            mismatched_epochs=mismatched,
            all_passed=all_passed,
            details=details,
        )


__all__ = ["ReplayReport", "ReplayReportGenerator"]
