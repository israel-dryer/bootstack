"""Shared date helpers for the date-picker composites."""
from __future__ import annotations

from datetime import date, datetime


def coerce_date(value: date | datetime | str | None) -> date | None:
    """Coerce a date, datetime, or date string to a plain `date`, or `None`.

    Accepts `date`/`datetime` instances (a `datetime` is narrowed to its
    `date`), `'YYYY-MM-DD'` or `'MM/DD/YYYY'` strings, and any ISO-8601 string.
    Returns `None` for `None` or anything unparseable.

    Args:
        value: The value to coerce.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
            try:
                return datetime.strptime(value, fmt).date()
            except Exception:
                continue
        try:
            return datetime.fromisoformat(value).date()
        except Exception:
            return None
    return None