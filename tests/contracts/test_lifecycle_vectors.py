from influx.contracts.lifecycle import ContractLifecycle


def test_register_contract():
    lifecycle = ContractLifecycle()

    lifecycle.register("contract_a")

    assert lifecycle.state("contract_a") == "registered"


def test_activate_contract():
    lifecycle = ContractLifecycle()

    lifecycle.register("contract_a")
    lifecycle.activate("contract_a")

    assert lifecycle.state("contract_a") == "active"


def test_suspend_and_reactivate():
    lifecycle = ContractLifecycle()

    lifecycle.register("contract_a")
    lifecycle.activate("contract_a")
    lifecycle.suspend("contract_a")
    lifecycle.activate("contract_a")

    assert lifecycle.state("contract_a") == "active"


def test_retire_contract():
    lifecycle = ContractLifecycle()

    lifecycle.register("contract_a")
    lifecycle.retire("contract_a")

    assert lifecycle.state("contract_a") == "retired"


def test_invalid_transition_fails():
    lifecycle = ContractLifecycle()

    lifecycle.register("contract_a")

    try:
        lifecycle.suspend("contract_a")
    except ValueError:
        assert True
    else:
        assert False


def test_snapshot_is_deterministic():
    lifecycle = ContractLifecycle()

    lifecycle.register("b")
    lifecycle.register("a")

    snapshot = lifecycle.snapshot()

    assert list(snapshot.keys()) == ["a", "b"]