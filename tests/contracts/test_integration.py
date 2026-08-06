"""
Integration tests for the smart contract runtime.
"""

from __future__ import annotations

from influx.contracts.runtime import ContractRuntime
from influx.contracts.context import ExecutionContext
from influx.contracts.storage import ContractStorage
from influx.contracts.gas import GasMeter
from influx.contracts.abi import ContractABI
from influx.contracts.events import EventEmitter
from influx.contracts.examples.counter import create_counter_contract
from influx.contracts.examples.token import create_token_contract
from influx.runtime.contract_integration import ContractRuntimeCoordinator


def test_counter_full_workflow() -> None:
    """Test the full counter contract workflow."""

    runtime = ContractRuntime()

    contract, handlers = create_counter_contract(
        contract_id="counter1",
        owner="alice",
        version="1.0.0",
    )

    runtime.register(contract)
    for handler in handlers:
        runtime.register_handler("counter1", handler)

    context = ExecutionContext(
        block_height=1,
        transaction_id="tx1",
        caller="alice",
        network_id="testnet",
    )

    storage = ContractStorage()
    gas_meter = GasMeter(limit=10000)
    events = EventEmitter()
    abi = ContractABI()

    result = runtime.execute(
        contract_id="counter1",
        function_name="get_count",
        context=context,
        storage=storage,
        gas_meter=gas_meter,
        abi=abi,
        events=events,
    )

    assert result == "0"

    result = runtime.execute(
        contract_id="counter1",
        function_name="increment",
        context=context,
        storage=storage,
        gas_meter=gas_meter,
        abi=abi,
        events=events,
        args=("5",),
    )

    assert result == "5"

    result = runtime.execute(
        contract_id="counter1",
        function_name="get_count",
        context=context,
        storage=storage,
        gas_meter=gas_meter,
        abi=abi,
        events=events,
    )

    assert result == "5"

    result = runtime.execute(
        contract_id="counter1",
        function_name="decrement",
        context=context,
        storage=storage,
        gas_meter=gas_meter,
        abi=abi,
        events=events,
        args=("2",),
    )

    assert result == "3"

    result = runtime.execute(
        contract_id="counter1",
        function_name="reset",
        context=context,
        storage=storage,
        gas_meter=gas_meter,
        abi=abi,
        events=events,
    )

    assert result == "0"


def test_token_transfer_workflow() -> None:
    """Test the full token contract workflow."""

    runtime = ContractRuntime()

    contract, handlers, initial_state = create_token_contract(
        contract_id="mytoken",
        owner="alice",
        version="1.0.0",
        initial_supply=1000000,
    )

    runtime.register(contract)
    for handler in handlers:
        runtime.register_handler("mytoken", handler)

    deploy_context = ExecutionContext(
        block_height=1,
        transaction_id="deploy_tx",
        caller="alice",
        network_id="testnet",
    )

    deploy_storage = ContractStorage()
    deploy_gas = GasMeter(limit=100000)
    deploy_events = EventEmitter()

    result = runtime.deploy(
        contract=contract,
        context=deploy_context,
        storage=deploy_storage,
        gas_meter=deploy_gas,
        events=deploy_events,
        initial_state=initial_state,
    )

    assert result.success

    context = ExecutionContext(
        block_height=2,
        transaction_id="tx_check",
        caller="alice",
        network_id="testnet",
    )

    storage = ContractStorage()
    gas_meter = GasMeter(limit=100000)
    events = EventEmitter()
    abi = ContractABI()

    total_supply = runtime.execute(
        contract_id="mytoken",
        function_name="total_supply",
        context=context,
        storage=storage,
        gas_meter=gas_meter,
        abi=abi,
        events=events,
    )

    assert total_supply == "1000000"

    balance = runtime.execute(
        contract_id="mytoken",
        function_name="balance_of",
        context=context,
        storage=storage,
        gas_meter=gas_meter,
        abi=abi,
        events=events,
        args=("alice",),
    )

    assert balance == "1000000"

    transfer_result = runtime.execute(
        contract_id="mytoken",
        function_name="transfer",
        context=context,
        storage=storage,
        gas_meter=gas_meter,
        abi=abi,
        events=events,
        args=("bob", "500"),
    )

    assert transfer_result == "success"

    alice_balance = runtime.execute(
        contract_id="mytoken",
        function_name="balance_of",
        context=context,
        storage=storage,
        gas_meter=gas_meter,
        abi=abi,
        events=events,
        args=("alice",),
    )

    assert alice_balance == "999500"

    bob_balance = runtime.execute(
        contract_id="mytoken",
        function_name="balance_of",
        context=context,
        storage=storage,
        gas_meter=gas_meter,
        abi=abi,
        events=events,
        args=("bob",),
    )

    assert bob_balance == "500"

    approve_result = runtime.execute(
        contract_id="mytoken",
        function_name="approve",
        context=context,
        storage=storage,
        gas_meter=gas_meter,
        abi=abi,
        events=events,
        args=("carol", "200"),
    )

    assert approve_result == "success"

    allowance = runtime.execute(
        contract_id="mytoken",
        function_name="allowance",
        context=context,
        storage=storage,
        gas_meter=gas_meter,
        abi=abi,
        events=events,
        args=("alice", "carol"),
    )

    assert allowance == "200"


def test_insufficient_balance() -> None:
    """Test insufficient balance error."""

    runtime = ContractRuntime()

    contract, handlers, initial_state = create_token_contract(
        contract_id="token2",
        owner="alice",
        initial_supply=100,
    )

    runtime.register(contract)
    for handler in handlers:
        runtime.register_handler("token2", handler)

    context = ExecutionContext(
        block_height=1,
        transaction_id="tx1",
        caller="alice",
        network_id="testnet",
    )

    storage = ContractStorage()
    gas_meter = GasMeter(limit=100000)
    events = EventEmitter()
    abi = ContractABI()

    runtime.deploy(
        contract,
        context,
        storage,
        gas_meter,
        events,
        initial_state,
    )

    result = runtime.execute(
        contract_id="token2",
        function_name="transfer",
        context=context,
        storage=storage,
        gas_meter=gas_meter,
        abi=abi,
        events=events,
        args=("bob", "200"),
    )

    assert result == "error: insufficient balance"


def test_gas_exhaustion() -> None:
    """Test gas exhaustion during execution."""

    runtime = ContractRuntime()

    contract, handlers = create_counter_contract()

    runtime.register(contract)
    for handler in handlers:
        runtime.register_handler("counter", handler)

    context = ExecutionContext(
        block_height=1,
        transaction_id="tx1",
        caller="alice",
        network_id="testnet",
    )

    storage = ContractStorage()
    gas_meter = GasMeter(limit=1)
    events = EventEmitter()
    abi = ContractABI()

    try:
        runtime.execute(
            contract_id="counter",
            function_name="increment",
            context=context,
            storage=storage,
            gas_meter=gas_meter,
            abi=abi,
            events=events,
            args=("5",),
        )
        assert False, "Expected gas exhaustion"
    except Exception:
        pass


def test_contract_integration_coordinator() -> None:
    """Test the contract integration coordinator."""

    coordinator = ContractRuntimeCoordinator()

    contract, handlers = create_counter_contract(
        contract_id="coord_counter",
        owner="system",
    )

    coordinator.register_contract(contract)
    for handler in handlers:
        coordinator.register_handler("coord_counter", handler)

    assert coordinator.contract_count() == 1
    assert coordinator.registered_contracts() == 1
