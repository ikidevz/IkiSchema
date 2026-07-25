from __future__ import annotations

import csv
import json
from pathlib import Path

from . import types as T
from .exceptions import SchemaInferenceError
from .utils import normalize_csv_value, null_ratio


def infer_pandas(df, include_stats: bool, samples: bool):
    from .schema import ColumnSchema

    cols = []
    n = len(df)
    for name in df.columns:
        series = df[name]
        nullable = bool(series.isna().any())
        null_count = int(series.isna().sum()) if include_stats else None
        null_ratio_value = null_ratio(null_count, n) if include_stats else None
        sample_values = list(series.dropna().head(
            5).tolist()) if samples else None
        dtype = T.normalize_pandas_dtype(
            series.dtype, sample_col=series.dropna().tolist())
        cols.append(ColumnSchema(name, dtype, nullable,
                    null_count, null_ratio_value, sample_values))
    return cols


def infer_polars(df, include_stats: bool, samples: bool):
    from .schema import ColumnSchema

    cols = []
    n = df.height
    for name, dtype in zip(df.columns, df.dtypes):
        norm_dtype = T.normalize_polars_dtype(dtype)
        series = df[name]
        nullable = bool(series.null_count() > 0)
        null_count = int(series.null_count()) if include_stats else None
        null_ratio_value = null_ratio(null_count, n) if include_stats else None
        sample_values = [v for v in series.drop_nulls().head(5)
                         ] if samples else None
        cols.append(ColumnSchema(name, norm_dtype, nullable,
                    null_count, null_ratio_value, sample_values))
    return cols


def infer_pyarrow(table, include_stats: bool, samples: bool):
    from .schema import ColumnSchema

    cols = []
    n = table.num_rows
    for field_ in table.schema:
        norm_dtype = T.normalize_pyarrow_dtype(field_.type)
        column = table[field_.name]
        nullable = field_.nullable
        null_count = None
        null_ratio_value = None
        sample_values = None
        if include_stats:
            null_count = int(column.null_count)
            null_ratio_value = null_ratio(null_count, n)
        if samples:
            sample_values = [value.as_py() if hasattr(
                value, "as_py") else value for value in column[:5].to_pylist()]
        cols.append(ColumnSchema(field_.name, norm_dtype, nullable,
                    null_count, null_ratio_value, sample_values))
    return cols


def infer_pyspark(df, include_stats: bool, samples: bool):
    from .schema import ColumnSchema

    cols = []
    for field_ in df.schema.fields:
        norm_dtype = T.normalize_pyspark_dtype(field_.dataType)
        cols.append(ColumnSchema(field_.name, norm_dtype,
                    field_.nullable, None, None, None))
    return cols


def infer_records(records: list[dict]):
    from .schema import ColumnSchema

    if not records:
        raise SchemaInferenceError(
            "from_records() requires at least one record")

    all_keys = []
    seen = set()
    for record in records:
        for key in record.keys():
            if key not in seen:
                seen.add(key)
                all_keys.append(key)

    cols = []
    for key in all_keys:
        values = [record.get(key) for record in records]
        non_null = [v for v in values if v is not None]
        nullable = any(v is None for v in values)
        dtype = T.normalize_json_value(non_null)
        cols.append(ColumnSchema(key, dtype, nullable))
    return cols


def infer_parquet(path_str: str):
    from .schema import ColumnSchema
    import pyarrow.parquet as pq

    schema = pq.read_schema(path_str)
    return [ColumnSchema(f.name, T.normalize_pyarrow_dtype(f.type), f.nullable) for f in schema]


def infer_csv(path_str: str, sample_rows: int | None):
    from .schema import ColumnSchema

    with open(path_str, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        raise SchemaInferenceError(f"No rows found in {path_str}")

    if sample_rows is not None:
        rows = rows[:sample_rows]

    cols = []
    for key in rows[0].keys():
        raw_values = [row.get(key) for row in rows]
        non_null = [v for v in raw_values if v is not None]
        nullable = any(v is None for v in raw_values)
        dtype = normalize_csv_value(non_null)
        cols.append(ColumnSchema(key, dtype, nullable))
    return cols


def infer_json(path_str: str, sample_rows: int | None):
    with open(path_str, encoding="utf-8") as handle:
        data = json.load(handle)

    if isinstance(data, dict):
        data = [data]
    if sample_rows is not None:
        data = data[:sample_rows]
    return infer_records(data)


def infer_excel(path_str: str):
    import pandas as pd

    df = pd.read_excel(path_str)
    return infer_pandas(df, include_stats=False, samples=False)


def infer_sql(engine, query: str):
    from .schema import ColumnSchema
    from sqlalchemy import text

    with engine.connect() as conn:
        result = conn.execute(text(query))

    columns = []
    for column in result.keys():
        columns.append(ColumnSchema(column, "unknown", True))
    return columns


def infer_duckdb_relation(relation):
    from .schema import ColumnSchema

    cols = []
    for name, duck_type in zip(relation.columns, relation.types):
        dtype = T.DUCKDB_TYPE_MAP.get(str(duck_type).upper(), "unknown")
        cols.append(ColumnSchema(name, dtype, True))
    return cols
