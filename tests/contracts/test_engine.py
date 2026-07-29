"""
Tests for the contract execution engine.
"""

from __future__ import annotations

from influx.contracts.engine import ContractEngine, FunctionHandler
from influx.contracts.contract import Contract
from influx.contracts.context import ExecutionContext
from influx.contracts.storage import ContractStorage
from influx.contracts.gas import GasMeter
from influx.contracts.abi import ContractABI
from influx.contracts.events import EventEmitter
from influx.contracts.exceptions import (
    ContractExecutionError,
    GasExhaustedError,
)


def test_engine_register_handler() -> None:
    """Test registering a function handler."""

    engine = ContractEngine()

    def my_handler(_storage, _context, **_kwargs):
        return "hello"

    handler = FunctionHandler(
        name="greet",
        handler=my_handler,
        gas_cost=5,
    )

    engine.register_handler("test_contract", handler)

    assert engine.registered_count() == 1
    assert engine.registered_count("test_contract") == 1
    assert engine.has_handler("test_contract", "greet")


def test_engine_dispatch() -> None:
    """Test dispatching a function call."""

    engine = ContractEngine()

    def greet_handler(*args, _storage, _context, _gas, _events, _abi, **kwargs):
        _gas.consume(5)
        return f"Hello, {args[0] if args else 'World'}!"

    handler = FunctionHandler(
        name="greet",
        handler=greet_handler,
        gas_cost=10,
    )

    contract = Contract(
        contract_id="test_contract",
        owner="alice",
        version="1.0.0",
        code_hash="0xabc123",
    )

    engine.register_handler("test_contract", handler)

    context = ExecutionContext(
        block_height=100,
        transaction_id="tx1",
        caller="alice",
        network_id="testnet",
    )

    storage = ContractStorage()
    gas_meter = GasMeter(limit=1000)
    events = EventEmitter()
    abi = ContractABI()

    result = engine.dispatch(
        contract=contract,
        function_name="greet",
        context=context,
        storage=storage,
        gas_meter=gas_meter,
        events=events,
        abi=abi,
        args=("Alice",),
    )

    assert result == "Hello, Alice!"
    assert gas_meter.consumed == 15  # 10 base + 5 from handler


def test_engine_missing_handler() -> None:
    """Test dispatching a non-existent handler."""

    engine = ContractEngine()

    contract = Contract(
        contract_id="test_contract",
        owner="alice",
        version="1.0.0",
        code_hash="0xabc123",
    )

    context = ExecutionContext(
        block_height=100,
        transaction_id="tx1",
        caller="alice",
        network_id="testnet",
    )

    storage = ContractStorage()
    gas_meter = GasMeter(limit=1000)
    events = EventEmitter()
    abi = ContractABI()

    try:
        engine.dispatch(
            contract=contract,
            function_name="nonexistent",
            context=context,
            storage=storage,
            gas_meter=gas_meter,
            events=events,
            abi=abi,
        )
        assert False, "Expected ContractExecutionError"
    except ContractExecutionError:
        pass


def test_engine_gas_exhaustion() -> None:
    """Test gas exhaustion during execution."""

    engine = ContractEngine()

    def expensive_handler(*args, _gas, **_kwargs):
        _gas.consume(500)
        return "done"

    handler = FunctionHandler(
        name="expensive",
        handler=expensive_handler,
        gas_cost=10,
    )

    contract = Contract(
        contract_id="test_contract",
        owner="alice",
        version="1.0.0",
        code_hash="0xabc123",
    )

    engine.register_handler("test_contract", handler)

    context = ExecutionContext(
        block_height=100,
        transaction_id="tx1",
        caller="alice",
        network_id="testnet",
    )

    storage = ContractStorage()
    gas_meter = GasMeter(limit=100)  # Low limit
    events = EventEmitter()
    abi = ContractABI()

    try:
        engine.dispatch(
            contract=contract,
            function_name="expensive",
            context=context,
            storage=storage,
            gas_meter=gas_meter,
            events=events,
            abi=abi,
        )
        assert False, "Expected GasExhaustedError"
    except GasExhaustedError:
        pass


def test_engine_clear_handlers() -> None:
    """Test clearing registered handlers."""

    engine = ContractEngine()

    def handler(*args, **_kwargs):
        return "ok"

    handler1 = FunctionHandler(name="fn1", handler=handler, gas_cost=5)
    handler2 = FunctionHandler(name="fn2", handler=handler, gas_cost=5)

    engine.register_handler("contract_a", handler1)
    engine.register_handler("contract_b", handler2)

    assert engine.registered_count() == 2

    engine.clear_handlers("contract_a")

    assert engine.registered_count() == 1
    assert not engine.has_handler("contract_a", "fn1")
    assert engine.has_handler("contract_b", "fn2")

    engine.clear_handlers()

    assert engine.registered_count() == 0


def test_engine_handler_execution_error() -> None:
    """Test handler raising an execution error."""

    engine = ContractEngine()

    def failing_handler(*args, **_kwargs):
        raise ValueError("Something went wrong")

    handler = FunctionHandler(
        name="fail",
        handler=failing_handler,
        gas_cost=5,
    )

    contract = Contract(
        contract_id="test_contract",
        owner="alice",
        version="1.0.0",
        code_hash="0xabc123",
    )

    engine.register_handler("test_contract", handler)

    context = ExecutionContext(
        block_height=100,
        transaction_id="tx1",
        caller="alice",
        network_id="testnet",
    )

    storage = ContractStorage()
    gas_meter = GasMeter(limit=1000)
    events = EventEmitter()
    abi = ContractABI()

    try:
        engine.dispatch(
            contract=contract,
            function_name="fail",
            context=context,
            storage=storage,
            gas_meter=gas_meter,
            events=events,
            abi=abi,
        )
        assert False, "Expected ContractExecutionError"
    except ContractExecutionError:
        pass


def test_engine_event_emission() -> None:
    """Test that execution emits events."""

    engine = ContractEngine()

    def handler(*args, _events, **_kwargs):
        _events.emit(
            type("Event", (), {"event_name": "custom", "contract_id": "test", "payload": {}})()
        )
        return "done"

    handler_obj = FunctionHandler(name="test", handler=handler, gas_cost=5)

    contract = Contract(
        contract_id="test_contract",
        owner="alice",
        version="1.0.0",
        code_hash="0xabc123",
    )

    engine.register_handler("test_contract", handler_obj)

    context = ExecutionContext(
        block_height=100,
        transaction_id="tx1",
        caller="alice",
        network_id="testnet",
    )

    storage = ContractStorage()
    gas_meter = GasMeter(limit=1000)
    events = EventEmitter()
    abi = ContractABI()

    engine.dispatch(
        contract=contract,
        function_name="test",
        context=context,
        storage=storage,
        gas_meter=gas_meter,
        events=events,
        abi=abi,
    )

    # Should have emitted at least 1 event (the function_executed event)
    assert events.count() >= 1
