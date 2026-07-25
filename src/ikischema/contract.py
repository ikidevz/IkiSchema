from __future__ import annotations

import json
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path

from .diff import SchemaDiff, Violation
from .exceptions import ContractLoadError, ContractViolationError
from .schema import ColumnSchema, Schema, coerce_to_schema

CONTRACT_FORMAT_VERSION = "1.0"


@dataclass(frozen=True)
class SchemaContract:
    schema: Schema
    strictness: dict | None = None
    created_at: str | None = None

    @classmethod
    def from_schema(cls, schema: Schema, strictness: dict | None = None) -> "SchemaContract":
        return cls(schema=schema, strictness=strictness or {}, created_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"))

    def save(self, path: str | Path) -> None:
        payload = {
            "ikischema_contract_version": CONTRACT_FORMAT_VERSION,
            "created_at": self.created_at,
            "strictness": self.strictness or {},
            "columns": [column.to_dict() for column in self.schema.columns],
        }
        Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "SchemaContract":
        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise ContractLoadError(
                f"Contract file not found: {path}") from exc
        except json.JSONDecodeError as exc:
            raise ContractLoadError(
                f"Contract JSON is invalid: {path}") from exc

        if payload.get("ikischema_contract_version") != CONTRACT_FORMAT_VERSION:
            raise ContractLoadError("Unsupported contract format version")

        columns = [ColumnSchema(**item) for item in payload.get("columns", [])]
        schema = Schema(columns=columns)
        return cls(schema=schema, strictness=payload.get("strictness", {}), created_at=payload.get("created_at"))

    def validate(self, source, raise_on_breaking: bool = False, **kwargs):
        source_schema = coerce_to_schema(source, **kwargs)
        diff_result = SchemaDiff.compare(
            self.schema,
            source_schema,
            ignore=kwargs.get("ignore"),
            ignore_case=kwargs.get("ignore_case", False),
            additions_are_breaking=bool(
                (self.strictness or {}).get("additions_are_breaking", False)),
            widening_is_breaking=bool(
                (self.strictness or {}).get("widening_is_breaking", False)),
        )

        violations = []
        for column in diff_result.removed:
            violations.append(Violation(column=column, change="column_removed",
                              expected="present", actual=None, severity="breaking"))
        for column in diff_result.added:
            severity = "breaking" if (self.strictness or {}).get(
                "additions_are_breaking", False) else "non_breaking"
            violations.append(Violation(column=column, change="column_added",
                              expected=None, actual="present", severity=severity))
        violations.extend(diff_result.type_changes)
        violations.extend(diff_result.nullability_changes)

        if raise_on_breaking and any(v.severity == "breaking" for v in violations):
            raise ContractViolationError(violations)
        return violations
