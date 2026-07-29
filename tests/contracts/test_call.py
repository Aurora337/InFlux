"""
Tests for the cross-contract call module.
"""

from __future__ import annotations

from influx.contracts.call import CallContext, CallStack
from influx.contracts.exceptions import ContractExecutionError


def test_call_stack_push_pop() -> None:
    """Test basic push and pop operations."""

    stack = CallStack()

    ctx = CallContext(
        caller="alice",
        contract_id="contract_a",
        function="transfer",
        value=100,
        gas_limit=1000,
    )

    stack.push(ctx)
    assert stack.depth() == 1
    assert not stack.is_empty()

    popped = stack.pop()
    assert popped == ctx
    assert stack.is_empty()


def test_call_stack_peek() -> None:
    """Test peeking at the top of the call stack."""

    stack = CallStack()

    assert stack.peek() is None

    ctx1 = CallContext(
        caller="alice",
        contract_id="contract_a",
        function="transfer",
    )

    ctx2 = CallContext(
        caller="contract_a",
        contract_id="contract_b",
        function="balance_of",
    )

    stack.push(ctx1)
    stack.push(ctx2)

    top = stack.peek()
    assert top is not None
    assert top.contract_id == "contract_b"
    assert top.function == "balance_of"


def test_call_stack_max_depth() -> None:
    """Test call depth limitation."""

    stack = CallStack(max_depth=3)

    ctx = CallContext(
        caller="alice",
        contract_id="test",
        function="fn",
    )

    stack.push(ctx)
    stack.push(ctx)
    stack.push(ctx)

    try:
        stack.push(ctx)
        assert False, "Expected ContractExecutionError for depth exceeded"
    except ContractExecutionError:
        pass


def test_reentrancy_detection() -> None:
    """Test reentrancy detection."""

    stack = CallStack()

    ctx_a = CallContext(
        caller="alice",
        contract_id="contract_a",
        function="transfer",
    )

    ctx_b = CallContext(
        caller="contract_a",
        contract_id="contract_b",
        function="callback",
    )

    stack.push(ctx_a)

    assert stack.is_reentrant("contract_a", "transfer")
    assert not stack.is_reentrant("contract_b", "callback")

    stack.push(ctx_b)

    assert stack.is_reentrant("contract_b", "callback")


def test_call_chain() -> None:
    """Test call chain retrieval."""

    stack = CallStack()

    ctx_a = CallContext(
        caller="alice",
        contract_id="contract_a",
        function="transfer",
        value=50,
    )

    ctx_b = CallContext(
        caller="contract_a",
        contract_id="contract_b",
        function="callback",
        value=0,
    )

    stack.push(ctx_a)
    stack.push(ctx_b)

    chain = stack.call_chain()

    assert len(chain) == 2
    assert chain[0]["contract_id"] == "contract_a"
    assert chain[1]["contract_id"] == "contract_b"


def test_call_stack_reset() -> None:
    """Test resetting the call stack."""

    stack = CallStack()

    ctx = CallContext(
        caller="alice",
        contract_id="test",
        function="fn",
    )

    stack.push(ctx)
    assert not stack.is_empty()

    stack.reset()
    assert stack.is_empty()
    assert stack.depth() == 0


def test_empty_stack_pop() -> None:
    """Test popping from an empty stack."""

    stack = CallStack()

    try:
        stack.pop()
        assert False, "Expected ContractExecutionError"
    except ContractExecutionError:
        pass
