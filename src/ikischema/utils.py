"""Small shared helpers used across inference and contract logic."""

from __future__ import annotations

_NON_NUMERIC_LITERALS = {"nan", "inf", "-inf",
                         "+inf", "infinity", "-infinity", "+infinity"}


def looks_like_int(token: str) -> bool:
    t = token.strip()
    if not t:
        return False
    if t[0] in "+-":
        t = t[1:]
    return t.isdigit()


def looks_like_float(token: str) -> bool:
    t = token.strip()
    if t.lower() in _NON_NUMERIC_LITERALS:
        return False
    if "_" in t:
        return False
    try:
        float(t)
        return True
    except ValueError:
        return False


def null_ratio(null_count: int, total: int) -> float | None:
    if total == 0:
        return None
    return null_count / total


def normalize_csv_value(values) -> str:
    saw_int = False
    saw_float = False
    saw_other = False

    for v in values:
        token = str(v).strip()
        if not token:
            continue
        if looks_like_int(token):
            saw_int = True
        elif looks_like_float(token):
            saw_float = True
        else:
            saw_other = True

    if saw_other:
        return "unknown" if (saw_int or saw_float) else "string"
    if saw_float:
        return "float64"
    if saw_int:
        return "int64"
    return "unknown"
