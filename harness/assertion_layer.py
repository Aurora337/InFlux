"""assertion_layer.py

Assertion utilities and invariant checks for harness tests.
"""

from typing import Any, Callable

class AssertionFailure(Exception):
    pass

class Assertions:
    @staticmethod
    def assert_equal(a: Any, b: Any, msg: str = "") -> None:
        if a != b:
            raise AssertionFailure(msg or f"{a} != {b}")

    @staticmethod
    def assert_true(cond: bool, msg: str = "") -> None:
        if not cond:
            raise AssertionFailure(msg or "Condition is not true")

__all__ = ["Assertions", "AssertionFailure"]