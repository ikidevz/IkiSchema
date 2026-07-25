from __future__ import annotations

from .contract import SchemaContract
from .diff import SchemaDiff
from .schema import Schema, coerce_to_schema


def infer(source, query: str | None = None, **kwargs) -> Schema:
    if query is not None:
        from .schema import Schema

        if hasattr(source, "connect"):
            return Schema.from_sql(source, query)
    return coerce_to_schema(source, **kwargs)


def diff(schema_a: Schema, schema_b: Schema, **kwargs) -> SchemaDiff:
    return SchemaDiff.compare(schema_a, schema_b, **kwargs)


def check(source, contract_path: str, **kwargs):
    contract = SchemaContract.load(contract_path)
    return contract.validate(source, **kwargs)
