from influx.contracts.runtime import ContractRuntime
from influx.contracts.context import ExecutionContext
from influx.contracts.storage import ContractStorage
from influx.contracts.gas import GasMeter
from influx.contracts.events import EventEmitter
from influx.contracts.abi import ContractABI
from influx.contracts.examples.counter import create_counter_contract

import pytest


def create_runtime():
    runtime = ContractRuntime()

    contract, handlers = create_counter_contract(
        contract_id="test_contract",
        owner="validator_001",
    )

    runtime.register(contract)

    for handler in handlers:
        runtime.register_handler(
            contract.contract_id,
            handler,
        )

    return runtime


def create_context():
    return ExecutionContext(
        network_id="influx-testnet",
        block_height=1,
        transaction_id="tx_001",
        caller="validator_001",
    )


def create_environment():
    return (
        ContractStorage(),
        GasMeter(limit=100),
        ContractABI(),
        EventEmitter(),
    )


def test_same_execution_produces_same_result():
    runtime_a = create_runtime()
    runtime_b = create_runtime()

    storage_a, gas_a, abi_a, events_a = create_environment()
    storage_b, gas_b, abi_b, events_b = create_environment()

    result_a = runtime_a.execute(
        contract_id="test_contract",
        function_name="get_count",
        context=create_context(),
        storage=storage_a,
        gas_meter=gas_a,
        abi=abi_a,
        events=events_a,
    )

    result_b = runtime_b.execute(
        contract_id="test_contract",
        function_name="get_count",
        context=create_context(),
        storage=storage_b,
        gas_meter=gas_b,
        abi=abi_b,
        events=events_b,
    )

    assert result_a == result_b


def test_execution_changes_storage_deterministically():
    runtime = create_runtime()

    storage, gas, abi, events = create_environment()

    runtime.execute(
        contract_id="test_contract",
        function_name="increment",
        context=create_context(),
        storage=storage,
        gas_meter=gas,
        abi=abi,
        events=events,
    )

    assert storage.get("count") == "1"


def test_registered_contract_count():
    runtime = create_runtime()

    assert runtime.registered() == 1


def test_duplicate_contract_registration_fails():
    runtime = create_runtime()

    contract, _ = create_counter_contract(
        contract_id="test_contract",
        owner="validator_001",
    )

    with pytest.raises(Exception):
        runtime.register(contract)


def test_missing_contract_fails():
    runtime = ContractRuntime()

    storage, gas, abi, events = create_environment()

    with pytest.raises(Exception):
        runtime.execute(
            contract_id="missing",
            function_name="get_count",
            context=create_context(),
            storage=storage,
            gas_meter=gas,
            abi=abi,
            events=events,
        )