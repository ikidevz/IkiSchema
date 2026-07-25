import json
import io
from contextlib import redirect_stdout

from ikischema import Schema, SchemaContract, infer
from ikischema.cli import main


def test_contract_can_enforce_breaking_additions(tmp_path):
    base_schema = infer([{"id": 1, "name": "Ada"}])
    contract = SchemaContract.from_schema(
        base_schema, strictness={"additions_are_breaking": True})
    contract_path = tmp_path / "contract.json"
    contract.save(contract_path)

    violations = SchemaContract.load(contract_path).validate(
        [{"id": 2, "name": "Grace", "score": 10.5}])

    assert any(v.change == "column_added" and v.severity ==
               "breaking" for v in violations)


def test_merge_marks_nullable_columns_and_conflicts():
    left = infer([{"id": 1, "name": "Ada"}])
    right = infer([{"id": 1, "score": 10.5}])

    merged = Schema.merge(left, right)

    assert "name" in merged.column_map()
    assert "score" in merged.column_map()

    assert merged.column_map()["name"].nullable is True
    assert merged.column_map()["score"].nullable is True
    assert merged.column_map()["id"].nullable is False


def test_cli_infer_outputs_schema(capsys):
    exit_code = main(["infer", json.dumps([{"id": 1, "name": "Ada"}])])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "id" in captured.out
    assert "name" in captured.out
