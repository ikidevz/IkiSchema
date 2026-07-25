"""Dtype normalization helpers for supported source types."""

from __future__ import annotations

NORMALIZED_DTYPES = {"string", "int64", "float64", "bool",
                     "datetime", "datetime_tz", "date", "binary", "unknown"}


def normalize_pandas_dtype(pd_dtype, sample_col=None) -> str:
    import pandas as pd

    if pd.api.types.is_datetime64tz_dtype(pd_dtype):
        return "datetime_tz"
    if pd.api.types.is_datetime64_any_dtype(pd_dtype):
        return "datetime"

    name = str(pd_dtype)
    if name.startswith(("int", "Int", "uint")):
        return "int64"
    if name.startswith("float"):
        return "float64"
    if name == "bool":
        return "bool"
    if name == "object":
        if sample_col is None:
            return "unknown"
        if any(isinstance(v, (str, bytes)) for v in sample_col):
            return "string"
        return "unknown"
    return "unknown"


def normalize_polars_dtype(pl_dtype) -> str:
    import polars as pl

    if pl_dtype in (pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64):
        return "int64"
    if pl_dtype in (pl.Float32, pl.Float64):
        return "float64"
    if pl_dtype == pl.Boolean:
        return "bool"
    if pl_dtype in (pl.Utf8,):
        return "string"
    if pl_dtype == pl.Date:
        return "date"
    if isinstance(pl_dtype, pl.Datetime):
        return "datetime_tz" if pl_dtype.time_zone else "datetime"
    return "unknown"


def normalize_pyarrow_dtype(pa_type) -> str:
    import pyarrow as pa

    if pa.types.is_integer(pa_type):
        return "int64"
    if pa.types.is_floating(pa_type):
        return "float64"
    if pa.types.is_boolean(pa_type):
        return "bool"
    if pa.types.is_string(pa_type) or pa.types.is_large_string(pa_type):
        return "string"
    if pa.types.is_timestamp(pa_type):
        return "datetime_tz" if pa_type.tz else "datetime"
    if pa.types.is_date(pa_type):
        return "date"
    if pa.types.is_binary(pa_type) or pa.types.is_large_binary(pa_type):
        return "binary"
    return "unknown"


def normalize_json_value(values) -> str:
    types_seen = set()
    for v in values:
        if v is None:
            continue
        if isinstance(v, bool):
            types_seen.add("bool")
        elif isinstance(v, int) and not isinstance(v, bool):
            types_seen.add("int64")
        elif isinstance(v, float):
            types_seen.add("float64")
        elif isinstance(v, str):
            types_seen.add("string")
        else:
            types_seen.add("unknown")

    if not types_seen:
        return "unknown"
    if types_seen == {"int64"}:
        return "int64"
    if types_seen <= {"int64", "float64"}:
        return "float64"
    if len(types_seen) == 1:
        return next(iter(types_seen))
    return "unknown"


SQL_TYPE_MAP = {
    "INTEGER": "int64",
    "BIGINT": "int64",
    "SMALLINT": "int64",
    "FLOAT": "float64",
    "NUMERIC": "float64",
    "DECIMAL": "float64",
    "DOUBLE": "float64",
    "VARCHAR": "string",
    "TEXT": "string",
    "CHAR": "string",
    "BOOLEAN": "bool",
    "TIMESTAMP": "datetime",
    "TIMESTAMPTZ": "datetime_tz",
    "DATE": "date",
    "BLOB": "binary",
    "BYTEA": "binary",
}

DUCKDB_TYPE_MAP = {
    "BIGINT": "int64",
    "INTEGER": "int64",
    "HUGEINT": "int64",
    "DOUBLE": "float64",
    "DECIMAL": "float64",
    "VARCHAR": "string",
    "BOOLEAN": "bool",
    "TIMESTAMP": "datetime",
    "TIMESTAMP WITH TIME ZONE": "datetime_tz",
    "DATE": "date",
    "BLOB": "binary",
}


def normalize_pyspark_dtype(spark_type) -> str:
    from pyspark.sql import types as pst

    if isinstance(spark_type, (pst.IntegerType, pst.LongType, pst.ShortType, pst.ByteType)):
        return "int64"
    if isinstance(spark_type, (pst.FloatType, pst.DoubleType, pst.DecimalType)):
        return "float64"
    if isinstance(spark_type, pst.BooleanType):
        return "bool"
    if isinstance(spark_type, pst.StringType):
        return "string"
    if isinstance(spark_type, pst.TimestampType):
        return "datetime_tz"
    if isinstance(spark_type, pst.DateType):
        return "date"
    if isinstance(spark_type, pst.BinaryType):
        return "binary"
    if isinstance(spark_type, (pst.ArrayType, pst.MapType, pst.StructType)):
        return "unknown"
    return "unknown"
