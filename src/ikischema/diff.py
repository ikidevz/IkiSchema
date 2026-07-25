from __future__ import annotations

from dataclasses import dataclass

from .schema import Schema

_WIDENING = {("int64", "float64")}
_TZ_MISMATCH = {("datetime", "datetime_tz"), ("datetime_tz", "datetime")}


@dataclass(frozen=True)
class Violation:
    column: str
    change: str
    expected: str | None = None
    actual: str | None = None
    severity: str = "non_breaking"

    def __str__(self) -> str:
        return f"{self.column}: {self.change} (expected={self.expected}, actual={self.actual})"


@dataclass(frozen=True)
class SchemaDiff:
    added: list[str]
    removed: list[str]
    type_changes: list[Violation]
    nullability_changes: list[Violation]
    breaking: bool

    @classmethod
    def compare(
        cls,
        schema_a: Schema,
        schema_b: Schema,
        ignore: list[str] | None = None,
        ignore_case: bool = False,
        additions_are_breaking: bool = False,
        widening_is_breaking: bool = False,
    ) -> "SchemaDiff":
        ignore = ignore or []
        left_map = {col.name: col for col in schema_a.columns}
        right_map = {col.name: col for col in schema_b.columns}

        if ignore_case:
            left_map = {col.name.lower(): col for col in schema_a.columns}
            right_map = {col.name.lower(): col for col in schema_b.columns}

        added = [
            name for name in right_map if name not in left_map and name not in ignore]
        removed = [
            name for name in left_map if name not in right_map and name not in ignore]

        type_changes = []
        nullability_changes = []

        for name in sorted(set(left_map) & set(right_map)):
            if name in ignore:
                continue
            left_col = left_map[name]
            right_col = right_map[name]
            if left_col.dtype != right_col.dtype:
                severity = "breaking"
                if (left_col.dtype, right_col.dtype) in _WIDENING and not widening_is_breaking:
                    severity = "non_breaking"
                elif (left_col.dtype, right_col.dtype) in _TZ_MISMATCH:
                    severity = "breaking"
                type_changes.append(
                    Violation(column=name, change="type_changed", expected=left_col.dtype,
                              actual=right_col.dtype, severity=severity)
                )
            if left_col.nullable != right_col.nullable:
                severity = "breaking" if left_col.nullable and not right_col.nullable else "non_breaking"
                nullability_changes.append(
                    Violation(column=name, change="nullability_changed", expected=str(
                        left_col.nullable), actual=str(right_col.nullable), severity=severity)
                )

        breaking = any(
            v.severity == "breaking" for v in type_changes + nullability_changes)
        if additions_are_breaking and added:
            breaking = True

        return cls(added=added, removed=removed, type_changes=type_changes, nullability_changes=nullability_changes, breaking=breaking)

    def summary(self) -> str:
        parts = []
        if self.breaking:
            parts.append("breaking")
        else:
            parts.append("non_breaking")
        if self.added:
            parts.append(f"added={self.added}")
        if self.removed:
            parts.append(f"removed={self.removed}")
        if self.type_changes:
            parts.append(f"type_changes={len(self.type_changes)}")
        if self.nullability_changes:
            parts.append(
                f"nullability_changes={len(self.nullability_changes)}")
        return "; ".join(parts)
