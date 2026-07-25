from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import infer as I
from .exceptions import SchemaInferenceError


@dataclass(frozen=True)
class ColumnSchema:
    name: str
    dtype: str
    nullable: bool
    null_count: int | None = None
    null_ratio: float | None = None
    sample_values: list | None = None

    def to_dict(self) -> dict:
        data = asdict(self)
        return {k: v for k, v in data.items() if not (v is None and k in {"null_count", "null_ratio", "sample_values"})}


@dataclass(frozen=True)
class Schema:
    columns: list[ColumnSchema]
    merge_conflicts: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [f"{'name':<20}{'type':<14}{'nullable'}"]
        for col in self.columns:
            lines.append(f"{col.name:<20}{col.dtype:<14}{str(col.nullable)}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {"columns": [c.to_dict() for c in self.columns]}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def fingerprint(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def column_map(self) -> dict[str, ColumnSchema]:
        return {c.name: c for c in self.columns}

    @classmethod
    def deserialize(cls, data: dict) -> "Schema":
        cols = [ColumnSchema(**c) for c in data["columns"]]
        return cls(columns=cols)

    def serialize(self) -> dict:
        return self.to_dict()

    @classmethod
    def merge(cls, *schemas: "Schema") -> "Schema":
        if not schemas:
            raise SchemaInferenceError("merge() requires at least one schema")

        merged = {}
        conflicts = []
        for schema in schemas:
            for column in schema.columns:
                if column.name not in merged:
                    merged[column.name] = [column]
                else:
                    merged[column.name].append(column)

        merged_columns = []
        for name, columns in merged.items():
            dtypes = {col.dtype for col in columns}
            if len(dtypes) > 1:
                conflicts.append(name)
            nullable = len(columns) < len(schemas) or any(
                col.nullable for col in columns)
            dtype = "unknown" if len(dtypes) > 1 else columns[0].dtype
            merged_columns.append(ColumnSchema(name, dtype, nullable))

        return cls(columns=merged_columns, merge_conflicts=conflicts)

    @classmethod
    def from_dataframe(cls, df, include_stats: bool = False, samples: bool = False) -> "Schema":
        module_name = type(df).__module__
        if module_name.startswith("pandas"):
            return cls(columns=I.infer_pandas(df, include_stats=include_stats, samples=samples))
        if module_name.startswith("polars"):
            return cls(columns=I.infer_polars(df, include_stats=include_stats, samples=samples))
        if module_name.startswith("pyarrow"):
            return cls(columns=I.infer_pyarrow(df, include_stats=include_stats, samples=samples))
        if module_name.startswith("pyspark"):
            return cls(columns=I.infer_pyspark(df, include_stats=include_stats, samples=samples))
        raise SchemaInferenceError(f"Unsupported dataframe type: {type(df)}")

    @classmethod
    def from_records(cls, records: list[dict]) -> "Schema":
        return cls(columns=I.infer_records(records))

    @classmethod
    def from_record(cls, record: dict) -> "Schema":
        return cls.from_records([record])

    @classmethod
    def from_path(cls, source: str | Path, sample_rows: int | None = None) -> "Schema":
        path = Path(source)
        suffix = path.suffix.lower()
        if suffix == ".parquet":
            return cls(columns=I.infer_parquet(str(path)))
        if suffix == ".csv":
            return cls(columns=I.infer_csv(str(path), sample_rows))
        if suffix == ".json":
            return cls(columns=I.infer_json(str(path), sample_rows))
        if suffix == ".xlsx":
            return cls(columns=I.infer_excel(str(path)))
        raise SchemaInferenceError(f"Unsupported file type: {suffix}")

    @classmethod
    def from_sql(cls, engine, query: str) -> "Schema":
        return cls(columns=I.infer_sql(engine, query))

    @classmethod
    def from_duckdb_relation(cls, relation) -> "Schema":
        return cls(columns=I.infer_duckdb_relation(relation))


def coerce_to_schema(source, **kwargs) -> Schema:
    if isinstance(source, Schema):
        return source
    if isinstance(source, dict):
        if "columns" in source:
            return Schema.deserialize(source)
        return Schema.from_record(source)
    if isinstance(source, (list, tuple)):
        if source and isinstance(source[0], dict):
            return Schema.from_records(list(source))
        raise SchemaInferenceError("List items must be dict records")
    if isinstance(source, (str, Path)):
        return Schema.from_path(source, sample_rows=kwargs.get("sample_rows"))
    if hasattr(source, "columns") and hasattr(source, "dtypes"):
        return Schema.from_dataframe(source)
    raise SchemaInferenceError(
        f"Don't know how to coerce type into a Schema: {type(source)}")
