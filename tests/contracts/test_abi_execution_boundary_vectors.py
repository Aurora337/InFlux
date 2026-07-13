from influx.contracts.abi import ContractABI, ContractFunction


def create_abi():
    abi = ContractABI()

    abi.register(
        ContractFunction(
            name="transfer",
            parameters=(
                "from",
                "to",
                "amount",
            ),
            return_type="bool",
        )
    )

    return abi


def test_abi_method_resolution_is_deterministic():
    abi_a = create_abi()
    abi_b = create_abi()

    function_a = abi_a.get("transfer")
    function_b = abi_b.get("transfer")

    assert function_a == function_b


def test_abi_argument_order_is_preserved():
    abi = create_abi()

    function = abi.get("transfer")

    assert function.parameters == (
        "from",
        "to",
        "amount",
    )


def test_invalid_abi_method_is_rejected():
    abi = create_abi()

    try:
        abi.get("unknown_method")
    except KeyError:
        assert True
    else:
        assert False


def test_abi_definition_is_stable():
    abi_a = create_abi()
    abi_b = create_abi()

    assert abi_a.functions == abi_b.functions


def test_abi_boundary_blocks_unexposed_methods():
    abi = create_abi()

    assert "transfer" in abi.functions
    assert "mint" not in abi.functions