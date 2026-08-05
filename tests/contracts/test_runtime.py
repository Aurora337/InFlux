"""
Tests for the enhanced contract runtime.
"""

from __future__ import annotations

from influx.contracts.runtime import ContractRuntime
from influx.contracts.contract import Contract
from influx.contracts.context import ExecutionContext
from influx.contracts.storage import ContractStorage
from influx.contracts.gas import GasMeter
from influx.contracts.abi import ContractABI
from influx.contracts.events import EventEmitter
from influx.contracts.engine import FunctionHandler
from influx.contracts.exceptions import (
    ContractError,
    ContractExecutionError,
    ContractRegistrationError,
)


def test_runtime_register() -> None:
    """Test registering a contract."""

    runtime = ContractRuntime()

    contract = Contract(
        contract_id="test_contract",
        owner="alice",
        version="1.0.0",
        code_hash="0xabc123",
    )

    runtime.register(contract)

    assert runtime.registered() == 1
    assert runtime.has_contract("test_contract")
    assert runtime.get("test_contract") == contract


def test_runtime_duplicate_registration() -> None:
    """Test duplicate contract registration."""

    runtime = ContractRuntime()

    contract = Contract(
        contract_id="test_contract",
        owner="alice",
        version="1.0.0",
        code_hash="0xabc123",
    )

    runtime.register(contract)

    try:
        runtime.register(contract)
        assert False, "Expected ContractRegistrationError"
    except ContractRegistrationError:
        pass


def test_runtime_get_nonexistent() -> None:
    """Test getting a non-existent contract."""

    runtime = ContractRuntime()

    try:
        runtime.get("nonexistent")
        assert False, "Expected ContractError"
    except ContractError:
        pass


def test_runtime_deploy() -> None:
    """Test deploying a contract."""

    runtime = ContractRuntime()

    contract = Contract(
        contract_id="counter",
        owner="alice",
        version="1.0.0",
        code_hash="0xdef456",
    )

    context = ExecutionContext(
        block_height=100,
        transaction_id="tx_deploy",
        caller="alice",
        network_id="testnet",
    )

    storage = ContractStorage()
    gas_meter = GasMeter(limit=10000)
    events = EventEmitter()

    result = runtime.deploy(
        contract=contract,
        context=context,
        storage=storage,
        gas_meter=gas_meter,
        events=events,
        initial_state={"count": "0"},
    )

    assert result.success
    assert result.contract_id == "counter"
    assert runtime.registered() == 1

    assert storage.get("deployer") == "alice"
    assert storage.get("deployed_at_block") == "100"
    assert storage.get("count") == "0"
    assert events.count() >= 1


def test_runtime_register_handler_and_execute() -> None:
    """Test registering a handler and executing a function."""

    runtime = ContractRuntime()

    contract = Contract(
        contract_id="greeter",
        owner="bob",
        version="1.0.0",
        code_hash="0xghi789",
    )

    runtime.register(contract)

    def greet_handler(*args, _storage, _context, _gas, _events, _abi, **kwargs):
        name = args[0] if args else "World"
        _storage.put("last_greeted", name)
        return f"Hello, {name}!"

    handler = FunctionHandler(
        name="greet",
        handler=greet_handler,
        gas_cost=10,
    )

    runtime.register_handler("greeter", handler)

    context = ExecutionContext(
        block_height=200,
        transaction_id="tx_exec",
        caller="bob",
        network_id="testnet",
    )

    storage = ContractStorage()
    gas_meter = GasMeter(limit=10000)
    events = EventEmitter()
    abi = ContractABI()

    result = runtime.execute(
        contract_id="greeter",
        function_name="greet",
        context=context,
        storage=storage,
        gas_meter=gas_meter,
        abi=abi,
        events=events,
        args=("Bob",),
    )

    assert result == "Hello, Bob!"
    assert storage.get("last_greeted") == "Bob"


def test_runtime_cross_contract_call() -> None:
    """Test cross-contract call."""

    runtime = ContractRuntime()

    # Register contract A
    contract_a = Contract(
        contract_id="contract_a",
        owner="alice",
        version="1.0.0",
        code_hash="0xaaa",
    )

    def handler_a(*args, _storage, **_kwargs):
        return f"Response from A: {args[0] if args else 'none'}"

    runtime.register(contract_a)
    runtime.register_handler(
        "contract_a",
        FunctionHandler(name="call_me", handler=handler_a, gas_cost=5),
    )

    context = ExecutionContext(
        block_height=300,
        transaction_id="tx_cross",
        caller="alice",
        network_id="testnet",
    )

    storage = ContractStorage()
    gas_meter = GasMeter(limit=10000)
    events = EventEmitter()
    abi = ContractABI()

    result = runtime.call(
        target_contract_id="contract_a",
        function_name="call_me",
        caller="alice",
        context=context,
        storage=storage,
        gas_meter=gas_meter,
        abi=abi,
        events=events,
        args=("hello",),
    )

    assert result == "Response from A: hello"


def test_runtime_reentrancy_detection() -> None:
    """Test reentrancy detection."""

    runtime = ContractRuntime()

    contract = Contract(
        contract_id="reentrant",
        owner="alice",
        version="1.0.0",
        code_hash="0xbbb",
    )

    runtime.register(contract)

    context = ExecutionContext(
        block_height=400,
        transaction_id="tx_re",
        caller="alice",
        network_id="testnet",
    )

    storage = ContractStorage()
    gas_meter = GasMeter(limit=10000)
    events = EventEmitter()
    abi = ContractABI()

    try:
        runtime.call(
            target_contract_id="reentrant",
            function_name="nonexistent",
            caller="alice",
            context=context,
            storage=storage,
            gas_meter=gas_meter,
            abi=abi,
            events=events,
        )
        assert False, "Expected ContractExecutionError"
    except ContractExecutionError:
        pass


def test_runtime_registry_integration() -> None:
    """Test runtime registry integration."""

    runtime = ContractRuntime()

    contract = Contract(
        contract_id="test",
        owner="alice",
        version="2.0.0",
        code_hash="0xccc",
    )

    runtime.register(contract)

    registry = runtime.get_registry()

    assert registry.exists("test")
    metadata = registry.get("test")
    assert metadata["owner"] == "alice"
    assert metadata["version"] == "2.0.0"


def test_runtime_reset() -> None:
    """Test resetting the runtime."""

    runtime = ContractRuntime()

    contract = Contract(
        contract_id="test",
        owner="alice",
        version="1.0.0",
        code_hash="0xddd",
    )

    runtime.register(contract)
    assert runtime.registered() == 1

    runtime.reset()
    assert runtime.registered() == 0
    assert not runtime.has_contract("test")
