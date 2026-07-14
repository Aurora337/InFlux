from influx.contracts.upgrade.record import UpgradeRecord


def create_record():
    return UpgradeRecord(
        contract_id="contract_a",
        previous_version="1.0.0",
        new_version="2.0.0",
        migration_id="migration_001",
        height=100,
    )


def test_record_creation():

    record = create_record()

    assert record.contract_id == "contract_a"


def test_record_export():

    record = create_record()

    data = record.to_dict()

    assert data["new_version"] == "2.0.0"
    assert data["height"] == 100


def test_version_change_detected():

    record = create_record()

    assert record.is_upgrade()


def test_same_version_is_not_upgrade():

    record = UpgradeRecord(
        contract_id="contract_a",
        previous_version="1.0.0",
        new_version="1.0.0",
        migration_id="migration_001",
        height=100,
    )

    assert not record.is_upgrade()


def test_records_are_deterministic():

    first = create_record()
    second = create_record()

    assert (
        first.to_dict()
        ==
        second.to_dict()
    )


def test_record_is_immutable():

    record = create_record()

    try:
        record.new_version = "3.0.0"
    except Exception:
        assert True
    else:
        assert False