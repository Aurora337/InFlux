from influx.contracts.abi import (
    ContractABI,
    ContractFunction,
)


def test_register_function() -> None:
    abi = ContractABI()

    function = ContractFunction(
        name="transfer",
        parameters=("to", "amount"),
        return_type="bool",
    )

    abi.register(function)

    assert abi.count() == 1
    assert abi.get("transfer") == function