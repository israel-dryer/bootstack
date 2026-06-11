"""Shared normalization for the selection family's option shape.

`Select`, `SelectButton`, `RadioGroup`, and `ToggleGroup` all accept the same
`Option` shape (a plain string, a `(text, value)` tuple, or an `OptionDict`).
This module turns any of those into a canonical `OptionRecord` so every widget
shares one coercion + validation path.
"""
from __future__ import annotations

from typing import Any, Iterable, NamedTuple

from bootstack.widgets.types import Option

# Keys an OptionDict may carry. `text` is required; `value` defaults to `text`.
_KNOWN_OPTION_KEYS = frozenset({"text", "value", "icon", "disabled"})


class OptionRecord(NamedTuple):
    """A normalized option — what every selection widget consumes internally."""

    text: str
    """Display label."""
    value: Any
    """Stored and emitted value."""
    extras: dict
    """Reserved per-option extras (e.g. `icon`, `disabled`); empty for now."""


def normalize_option(opt: Option) -> OptionRecord:
    """Coerce a single `Option` to an `OptionRecord`.

    Args:
        opt: A plain string, a `(text, value)` tuple, or an `OptionDict`.

    Returns:
        The normalized `(text, value, extras)` record.

    Raises:
        TypeError: If `opt` is not a string, 2-tuple, or dict, or if a dict
            `text` is not a string.
        ValueError: If a tuple does not have exactly two items, or a dict is
            missing `text` or carries an unknown key.
    """
    if isinstance(opt, str):
        return OptionRecord(opt, opt, {})

    if isinstance(opt, dict):
        if "text" not in opt:
            raise ValueError(f"option dict is missing the required 'text' key: {opt!r}")
        unknown = set(opt) - _KNOWN_OPTION_KEYS
        if unknown:
            raise ValueError(
                f"option dict has unknown key(s) {sorted(unknown)}: {opt!r} "
                f"(allowed: {sorted(_KNOWN_OPTION_KEYS)})"
            )
        text = opt["text"]
        if not isinstance(text, str):
            raise TypeError(f"option 'text' must be a string, got {type(text).__name__}: {opt!r}")
        value = opt["value"] if "value" in opt else text
        extras = {k: opt[k] for k in opt if k not in ("text", "value")}
        return OptionRecord(text, value, extras)

    if isinstance(opt, tuple):
        if len(opt) != 2:
            raise ValueError(f"option tuple must be (text, value), got {len(opt)} items: {opt!r}")
        text, value = opt
        if not isinstance(text, str):
            raise TypeError(f"option text must be a string, got {type(text).__name__}: {opt!r}")
        return OptionRecord(text, value, {})

    raise TypeError(
        f"option must be a str, (text, value) tuple, or dict, got {type(opt).__name__}: {opt!r}"
    )


def normalize_options(opts: Iterable[Option] | None) -> list[OptionRecord]:
    """Coerce an iterable of `Option` values to a list of `OptionRecord`.

    Args:
        opts: Options to normalize, or `None` for an empty list.
    """
    if not opts:
        return []
    return [normalize_option(opt) for opt in opts]


def record_to_dict(record: OptionRecord) -> dict:
    """Render an `OptionRecord` as a public `{'text', 'value', ...extras}` dict."""
    return {"text": record.text, "value": record.value, **record.extras}