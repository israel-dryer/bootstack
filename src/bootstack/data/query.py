"""Expressive, SQL-free filtering and sorting for data sources.

Build filter conditions with `col` and combine them with the usual operators::

    from bootstack.data import col

    ds.where(col("age") >= 25)
    ds.where((col("status") == "active") & col("name").contains("ada"))
    ds.where(col("department").is_in(["Sales", "Engineering"]))
    ds.order("-salary", "name")          # '-' prefix sorts descending

A condition is backend-agnostic: in-memory sources evaluate it with
`matches()`, while SQLite renders it to a parameterized query with `to_sql()`
(values are always bound, never interpolated, so user input can't inject SQL).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Mapping, Sequence, Tuple, Union

__all__ = [
    "col",
    "Column",
    "Condition",
    "SortKey",
    "any_of",
    "all_of",
]


# ---------------------------------------------------------------------------
# SQL rendering helpers
# ---------------------------------------------------------------------------

_SQL_OPS = {"eq": "=", "ne": "!=", "lt": "<", "le": "<=", "gt": ">", "ge": ">="}


def _quote(identifier: str) -> str:
    """Quote a column identifier for safe use in SQL."""
    return '"' + str(identifier).replace('"', '""') + '"'


def _escape_like(value: str) -> str:
    """Escape LIKE wildcards so they match literally (paired with ESCAPE '\\')."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


SqlFragment = Tuple[str, List[Any]]


# ---------------------------------------------------------------------------
# Conditions
# ---------------------------------------------------------------------------

class Condition:
    """A filter expression. Combine with `&` (and), `|` (or), and `~` (not)."""

    def __and__(self, other: "Condition") -> "Condition":
        return And([self, other])

    def __or__(self, other: "Condition") -> "Condition":
        return Or([self, other])

    def __invert__(self) -> "Condition":
        return Not(self)

    def matches(self, row: Mapping[str, Any]) -> bool:
        """Return whether `row` satisfies this condition (in-memory evaluation)."""
        raise NotImplementedError

    def to_sql(self) -> SqlFragment:
        """Render to a parameterized SQL fragment: `(clause, params)`."""
        raise NotImplementedError


@dataclass
class Compare(Condition):
    """A value comparison: `column <op> value`."""

    column: str
    op: str  # eq, ne, lt, le, gt, ge
    value: Any

    def matches(self, row: Mapping[str, Any]) -> bool:
        actual = row.get(self.column)
        if self.op == "eq":
            return actual == self.value
        if self.op == "ne":
            return actual != self.value
        if actual is None or self.value is None:
            return False
        try:
            if self.op == "lt":
                return actual < self.value
            if self.op == "le":
                return actual <= self.value
            if self.op == "gt":
                return actual > self.value
            if self.op == "ge":
                return actual >= self.value
        except TypeError:
            return False
        return False

    def to_sql(self) -> SqlFragment:
        q = _quote(self.column)
        if self.value is None and self.op in ("eq", "ne"):
            return (f"{q} IS NULL" if self.op == "eq" else f"{q} IS NOT NULL", [])
        return (f"{q} {_SQL_OPS[self.op]} ?", [self.value])


@dataclass
class Match(Condition):
    """A case-insensitive text match: contains / startswith / endswith."""

    column: str
    kind: str  # contains, startswith, endswith
    value: str

    def matches(self, row: Mapping[str, Any]) -> bool:
        actual = row.get(self.column)
        if actual is None:
            return False
        haystack = str(actual).lower()
        needle = str(self.value).lower()
        if self.kind == "contains":
            return needle in haystack
        if self.kind == "startswith":
            return haystack.startswith(needle)
        if self.kind == "endswith":
            return haystack.endswith(needle)
        return False

    def to_sql(self) -> SqlFragment:
        esc = _escape_like(str(self.value))
        pattern = {
            "contains": f"%{esc}%",
            "startswith": f"{esc}%",
            "endswith": f"%{esc}",
        }[self.kind]
        return (f"{_quote(self.column)} LIKE ? ESCAPE '\\'", [pattern])


@dataclass
class In(Condition):
    """Membership test: `column IN (values)`."""

    column: str
    values: List[Any]

    def matches(self, row: Mapping[str, Any]) -> bool:
        return row.get(self.column) in self.values

    def to_sql(self) -> SqlFragment:
        if not self.values:
            return ("0", [])  # IN () matches nothing
        placeholders = ", ".join("?" for _ in self.values)
        return (f"{_quote(self.column)} IN ({placeholders})", list(self.values))


@dataclass
class IsNull(Condition):
    """Null test: `column IS NULL`."""

    column: str

    def matches(self, row: Mapping[str, Any]) -> bool:
        return row.get(self.column) is None

    def to_sql(self) -> SqlFragment:
        return (f"{_quote(self.column)} IS NULL", [])


@dataclass
class And(Condition):
    """All sub-conditions must hold."""

    parts: List[Condition] = field(default_factory=list)

    def matches(self, row: Mapping[str, Any]) -> bool:
        return all(p.matches(row) for p in self.parts)

    def to_sql(self) -> SqlFragment:
        return _combine(self.parts, " AND ", empty="1")


@dataclass
class Or(Condition):
    """At least one sub-condition must hold."""

    parts: List[Condition] = field(default_factory=list)

    def matches(self, row: Mapping[str, Any]) -> bool:
        return any(p.matches(row) for p in self.parts)

    def to_sql(self) -> SqlFragment:
        return _combine(self.parts, " OR ", empty="0")


@dataclass
class Not(Condition):
    """Negates a condition."""

    part: Condition

    def matches(self, row: Mapping[str, Any]) -> bool:
        return not self.part.matches(row)

    def to_sql(self) -> SqlFragment:
        clause, params = self.part.to_sql()
        return (f"NOT ({clause})", params)


def _combine(parts: Sequence[Condition], joiner: str, *, empty: str) -> SqlFragment:
    if not parts:
        return (empty, [])
    clauses: List[str] = []
    params: List[Any] = []
    for part in parts:
        clause, p = part.to_sql()
        clauses.append(clause)
        params.extend(p)
    return ("(" + joiner.join(clauses) + ")", params)


# ---------------------------------------------------------------------------
# Column reference (builds conditions / sort keys)
# ---------------------------------------------------------------------------

class Column:
    """A reference to a column. Build conditions and sort keys from it.

    Created by `col(name)`. Supports the comparison operators (`==`, `!=`,
    `<`, `<=`, `>`, `>=`), text matching (`contains`, `startswith`, `endswith`),
    membership (`is_in`), null tests (`is_null`, `is_not_null`), and sort
    direction (`asc`, `desc`).
    """

    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        self.name = name

    # comparisons
    def __eq__(self, other: Any) -> Condition:  # type: ignore[override]
        return Compare(self.name, "eq", other)

    def __ne__(self, other: Any) -> Condition:  # type: ignore[override]
        return Compare(self.name, "ne", other)

    def __lt__(self, other: Any) -> Condition:
        return Compare(self.name, "lt", other)

    def __le__(self, other: Any) -> Condition:
        return Compare(self.name, "le", other)

    def __gt__(self, other: Any) -> Condition:
        return Compare(self.name, "gt", other)

    def __ge__(self, other: Any) -> Condition:
        return Compare(self.name, "ge", other)

    __hash__ = None  # type: ignore[assignment]

    # text
    def contains(self, value: str) -> Condition:
        """Case-insensitive substring match."""
        return Match(self.name, "contains", value)

    def startswith(self, value: str) -> Condition:
        """Case-insensitive prefix match."""
        return Match(self.name, "startswith", value)

    def endswith(self, value: str) -> Condition:
        """Case-insensitive suffix match."""
        return Match(self.name, "endswith", value)

    # set / null
    def is_in(self, values: Sequence[Any]) -> Condition:
        """Match any value in `values`."""
        return In(self.name, list(values))

    def is_null(self) -> Condition:
        """Match rows where this column is null/missing."""
        return IsNull(self.name)

    def is_not_null(self) -> Condition:
        """Match rows where this column is not null."""
        return Not(IsNull(self.name))

    # sort
    def asc(self) -> "SortKey":
        """Sort by this column, ascending."""
        return SortKey(self.name, False)

    def desc(self) -> "SortKey":
        """Sort by this column, descending."""
        return SortKey(self.name, True)

    def __repr__(self) -> str:
        return f"col({self.name!r})"


def col(name: str) -> Column:
    """Reference a column by name for use in `where()` / `order()`."""
    return Column(name)


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------

@dataclass
class SortKey:
    """A single sort term: a column and a direction."""

    column: str
    descending: bool = False


SortSpec = Union[str, Column, SortKey]


def normalize_sort_keys(keys: Sequence[SortSpec]) -> List[SortKey]:
    """Normalize mixed sort specs into a list of `SortKey`.

    Accepts `"name"` (ascending), `"-name"` (descending), a `Column`
    (ascending), or a `SortKey`.
    """
    result: List[SortKey] = []
    for key in keys:
        if isinstance(key, SortKey):
            result.append(key)
        elif isinstance(key, Column):
            result.append(SortKey(key.name, False))
        elif isinstance(key, str):
            if key.startswith("-"):
                result.append(SortKey(key[1:], True))
            else:
                result.append(SortKey(key, False))
        else:
            raise TypeError(f"Invalid sort key: {key!r}")
    return result


# ---------------------------------------------------------------------------
# Combinators
# ---------------------------------------------------------------------------

def any_of(*conditions: Condition) -> Condition | None:
    """Combine conditions with OR. Returns None if none are given."""
    parts = [c for c in conditions if c is not None]
    if not parts:
        return None
    if len(parts) == 1:
        return parts[0]
    return Or(parts)


def all_of(*conditions: Condition) -> Condition | None:
    """Combine conditions with AND. Returns None if none are given."""
    parts = [c for c in conditions if c is not None]
    if not parts:
        return None
    if len(parts) == 1:
        return parts[0]
    return And(parts)
