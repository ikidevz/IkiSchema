import json
from pathlib import Path

from ikischema import SchemaContract, check, diff, infer


def test_infer_from_records_and_contract_round_trip(tmp_path):
    records = [
        {"id": 1, "name": "Ada", "score": 10.5},
        {"id": 2, "name": "Grace", "score": 20.0},
    ]

    schema = infer(records)

    assert schema.columns[0].name == "id"
    assert schema.columns[0].dtype == "int64"
    assert schema.columns[1].dtype == "string"
    assert schema.columns[2].dtype == "float64"

    contract = SchemaContract.from_schema(schema)
    path = tmp_path / "contract.json"
    contract.save(path)

    loaded = SchemaContract.load(path)
    assert loaded.schema.to_dict() == schema.to_dict()

    violations = loaded.validate(records)
    assert violations == []


def test_diff_reports_added_removed_and_nullability_changes():
    left = infer([{"id": 1, "name": "Ada"}, {"id": 2, "name": "Grace"}])
    right = infer([{"id": 1, "name": "Ada", "score": 10.5}, {
                  "id": 2, "name": "Grace", "score": 20.0}])

    result = diff(left, right)

    assert "score" in result.added
    assert result.breaking is False


def test_facade_check_uses_contract_file(tmp_path):
    contract_path = tmp_path / "contract.json"
    schema = infer([{"id": 1, "name": "Ada"}])
    SchemaContract.from_schema(schema).save(contract_path)

    violations = check([{"id": 2, "name": "Grace"}], contract_path)
    assert violations == []
