from influx.vm.exceptions import (
    ProgramValidationError,
    VMError,
)


def test_vm_error():

    error = VMError("failure")

    assert str(error) == "failure"


def test_program_validation_error():

    error = ProgramValidationError("invalid")

    assert str(error) == "invalid"


def test_program_validation_is_vm_error():

    assert issubclass(
        ProgramValidationError,
        VMError,
    )