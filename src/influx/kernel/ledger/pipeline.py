from typing import Any


def process_pipeline(state: Any, block: Any = None) -> Any:
    """
    Minimal ledger pipeline used by replay,
    validator, consensus, and simulation tests.
    """

    if block is not None and hasattr(state, "apply"):
        state.apply(block)

    return state
