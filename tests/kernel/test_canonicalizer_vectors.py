from influx.kernel.canonicalizer import Canonicalizer


def test_primitive_preservation():
    assert Canonicalizer.normalize(None) is None
    assert Canonicalizer.normalize("influx") == "influx"
    assert Canonicalizer.normalize(100) == 100
    assert Canonicalizer.normalize(1.25) == 1.25
    assert Canonicalizer.normalize(True) is True


def test_dictionary_ordering():
    first = {
        "b": 2,
        "a": 1,
    }

    second = {
        "a": 1,
        "b": 2,
    }

    assert Canonicalizer.normalize(first) == Canonicalizer.normalize(second)


def test_nested_structure_normalization():
    state_one = {
        "state": {
            "validators": [
                "validator_a",
                "validator_b",
            ]
        }
    }

    state_two = {
        "state": {
            "validators": [
                "validator_a",
                "validator_b",
            ]
        }
    }

    assert Canonicalizer.normalize(state_one) == Canonicalizer.normalize(state_two)


def test_set_normalization():
    first = {"a", "b", "c"}
    second = {"c", "a", "b"}

    assert Canonicalizer.normalize(first) == Canonicalizer.normalize(second)


def test_forbidden_fields_are_removed():
    state = {
        "height": 10,
        "timestamp": 123456,
        "time": 123456,
        "trace": "debug",
        "logs": ["entry"],
        "debug": True,
        "replay": "data",
        "metrics": {},
    }

    cleaned = Canonicalizer.strip_non_deterministic_fields(state)

    assert cleaned == {
        "height": 10,
    }


def test_canonical_output_stability():
    state = {
        "b": 2,
        "a": 1,
        "nested": {
            "value": 100,
        },
    }

    first = Canonicalizer.build(state)
    second = Canonicalizer.build(state)

    assert first == second