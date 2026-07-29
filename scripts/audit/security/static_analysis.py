"""
Static Analysis for InFlux Security Audit.

Runs static analysis tools and checks for common security issues.
"""

import ast
import os
import sys
from pathlib import Path


class SecurityIssue:
    """Represents a security issue found during analysis."""

    def __init__(self, file: str, line: int, severity: str, message: str):
        self.file = file
        self.line = line
        self.severity = severity
        self.message = message

    def to_dict(self) -> dict:
        return {
            "file": self.file,
            "line": self.line,
            "severity": self.severity,
            "message": self.message,
        }


class StaticAnalyzer:
    """Performs static analysis on InFlux source code."""

    def __init__(self, source_dir: str = "src"):
        self.source_dir = Path(source_dir)
        self.issues: list[SecurityIssue] = []

    def run_all(self) -> list[SecurityIssue]:
        """Run all static analysis checks."""
        self._check_import_security()
        self._check_exec_calls()
        self._check_eval_calls()
        self._check_subprocess_usage()
        self._check_hardcoded_secrets()
        self._check_insecure_deserialization()
        self._check_path_traversal()
        return self.issues

    def _check_import_security(self) -> None:
        """Check for potentially dangerous imports."""
        dangerous_imports = {
            "pickle": "Insecure deserialization",
            "shelve": "Insecure deserialization",
            "marshal": "Insecure deserialization",
            "cPickle": "Insecure deserialization",
            "telnetlib": "Unencrypted protocol",
            "ftplib": "Unencrypted protocol",
        }
        for py_file in self.source_dir.rglob("*.py"):
            try:
                with open(py_file) as f:
                    content = f.read()
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name in dangerous_imports:
                                rel_path = py_file.relative_to(self.source_dir.parent)
                                self.issues.append(SecurityIssue(
                                    file=str(rel_path),
                                    line=node.lineno,
                                    severity="HIGH",
                                    message=f"Dangerous import '{alias.name}': {dangerous_imports[alias.name]}",
                                ))
                    elif isinstance(node, ast.ImportFrom):
                        if node.module in dangerous_imports:
                            rel_path = py_file.relative_to(self.source_dir.parent)
                            self.issues.append(SecurityIssue(
                                file=str(rel_path),
                                line=node.lineno,
                                severity="HIGH",
                                message=f"Dangerous import '{node.module}': {dangerous_imports[node.module]}",
                            ))
            except (SyntaxError, UnicodeDecodeError):
                continue

    def _check_exec_calls(self) -> None:
        """Check for dangerous exec/eval calls."""
        for py_file in self.source_dir.rglob("*.py"):
            try:
                with open(py_file) as f:
                    content = f.read()
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name) and node.func.id in ("exec", "eval", "compile"):
                            rel_path = py_file.relative_to(self.source_dir.parent)
                            self.issues.append(SecurityIssue(
                                file=str(rel_path),
                                line=node.lineno,
                                severity="CRITICAL",
                                message=f"Dangerous call to '{node.func.id}()'",
                            ))
            except (SyntaxError, UnicodeDecodeError):
                continue

    def _check_eval_calls(self) -> None:
        """Check for eval/exec usage."""
        self._check_exec_calls()

    def _check_subprocess_usage(self) -> None:
        """Check for subprocess usage without shell=False."""
        for py_file in self.source_dir.rglob("*.py"):
            try:
                with open(py_file) as f:
                    content = f.read()
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Attribute):
                            if node.func.attr in ("Popen", "call", "run", "check_call", "check_output"):
                                for kw in node.keywords:
                                    if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value:
                                        rel_path = py_file.relative_to(self.source_dir.parent)
                                        self.issues.append(SecurityIssue(
                                            file=str(rel_path),
                                            line=node.lineno,
                                            severity="HIGH",
                                            message="Subprocess call with shell=True is dangerous",
                                        ))
            except (SyntaxError, UnicodeDecodeError):
                continue

    def _check_hardcoded_secrets(self) -> None:
        """Check for hardcoded secrets and passwords."""
        patterns = [
            "password", "secret", "api_key", "api-key", "apikey",
            "auth_token", "auth-token", "private_key", "private-key",
        ]
        for py_file in self.source_dir.rglob("*.py"):
            try:
                with open(py_file) as f:
                    lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if stripped.startswith("#") or stripped.startswith('"""'):
                        continue
                    lower = stripped.lower()
                    for pattern in patterns:
                        if pattern in lower and "=" in stripped:
                            value = stripped.split("=", 1)[1].strip().strip('"').strip("'")
                            if value and not value.startswith("os.") and not value.startswith("env"):
                                rel_path = py_file.relative_to(self.source_dir.parent)
                                self.issues.append(SecurityIssue(
                                    file=str(rel_path),
                                    line=i,
                                    severity="MEDIUM",
                                    message=f"Possible hardcoded {pattern}",
                                ))
            except UnicodeDecodeError:
                continue

    def _check_insecure_deserialization(self) -> None:
        """Check for insecure deserialization patterns."""
        for py_file in self.source_dir.rglob("*.py"):
            try:
                with open(py_file) as f:
                    content = f.read()
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Attribute):
                            if node.func.attr in ("loads", "load") and isinstance(node.func.value, ast.Name):
                                if node.func.value.id in ("pickle", "shelve", "marshal"):
                                    rel_path = py_file.relative_to(self.source_dir.parent)
                                    self.issues.append(SecurityIssue(
                                        file=str(rel_path),
                                        line=node.lineno,
                                        severity="HIGH",
                                        message=f"Insecure deserialization via {node.func.value.id}",
                                    ))
            except (SyntaxError, UnicodeDecodeError):
                continue

    def _check_path_traversal(self) -> None:
        """Check for path traversal vulnerabilities."""
        for py_file in self.source_dir.rglob("*.py"):
            try:
                with open(py_file) as f:
                    content = f.read()
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Attribute) and node.func.attr in ("open", "read_text", "write_text"):
                            for arg in node.args:
                                if isinstance(arg, ast.Name) and arg.id in ("path", "filepath", "filename"):
                                    rel_path = py_file.relative_to(self.source_dir.parent)
                                    self.issues.append(SecurityIssue(
                                        file=str(rel_path),
                                        line=node.lineno,
                                        severity="LOW",
                                        message="Potential path traversal with user input",
                                    ))
            except (SyntaxError, UnicodeDecodeError):
                continue

    def report(self) -> dict:
        """Generate a security analysis report."""
        by_severity = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for issue in self.issues:
            by_severity[issue.severity] = by_severity.get(issue.severity, 0) + 1

        return {
            "total_issues": len(self.issues),
            "by_severity": by_severity,
            "issues": [i.to_dict() for i in self.issues],
            "status": "PASS" if not any(
                i.severity in ("CRITICAL", "HIGH") for i in self.issues
            ) else "FAIL",
        }


def main() -> int:
    analyzer = StaticAnalyzer()
    issues = analyzer.run_all()
    report = analyzer.report()

    import json
    print(json.dumps(report, indent=2))

    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
