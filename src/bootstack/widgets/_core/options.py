"""Shared normalization for the selection family's option shape.

`Select`, `SelectButton`, `RadioGroup`, and `ToggleGroup` all accept the same
`Option` shape (a plain string, a `(text, value)` tuple, or an `OptionDict`).
This module turns any of those into a canonical `OptionRecord` so every widget
shares one coercion + validation path.
"""
from __future__ import annotations

from typing import Any, Iterable, NamedTuple

from bootstack.widgets.types import Option


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

    The dict form is a *data bag*: `text` is required (and `value` defaults to
    it) UNLESS the dict carries an `icon` and a `value`, in which case `text` may
    be omitted to request an icon-only option (`text` becomes `''`). `text`/
    `value` and the recognized `icon`/`disabled` act on rendering; every other
    key rides along as carried data, retrievable via the widget's `selection`.
    Unrecognized keys are NOT rejected — the dict route is opt-in, so the caller
    accepts the risk of a mistyped key.

    Args:
        opt: A plain string, a `(text, value)` tuple, or an `OptionDict`.

    Returns:
        The normalized `(text, value, extras)` record.

    Raises:
        TypeError: If `opt` is not a string, 2-tuple, or dict, or if a dict
            `text` is not a string.
        ValueError: If a tuple does not have exactly two items, or a dict has
            neither a `text` key nor an `icon` + `value` pair.
    """
    if isinstance(opt, str):
        return OptionRecord(opt, opt, {})

    if isinstance(opt, dict):
        if "text" in opt:
            text = opt["text"]
            if not isinstance(text, str):
                raise TypeError(f"option 'text' must be a string, got {type(text).__name__}: {opt!r}")
        elif "icon" in opt and "value" in opt:
            # Icon-only option: the label is omitted on purpose. The widget
            # renders the glyph alone and infers icon-only from the empty text.
            text = ""
        else:
            raise ValueError(
                "option dict needs a 'text' key (or 'icon' + 'value' for an "
                f"icon-only option): {opt!r}"
            )
        value = opt["value"] if "value" in opt else text
        # The bag: every key except text/value, including the reserved
        # icon/disabled (carried now, interpreted by the widget later).
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


def record_field(record: OptionRecord, field: str) -> Any:
    """Read one field from a record by name, spanning `text`/`value`/extras.

    The record is treated as the flat `{'text', 'value', ...extras}` bag, so a
    grouping or display selector can name any carried key (including `text` or
    `value`).

    Args:
        record: The normalized option record.
        field: The key to read.

    Returns:
        The field's value, or `None` when the record does not carry it.
    """
    if field == "text":
        return record.text
    if field == "value":
        return record.value
    return record.extras.get(field)


def cluster_records(
    records: list[OptionRecord], group_by: str | None
) -> list[tuple[str | None, list[OptionRecord]]]:
    """Cluster records into groups by a named bag field, for presentation.

    Buckets appear in **first-appearance** order — the order each distinct group
    value is first seen while walking `records`. Within a bucket the source
    order is preserved. A record whose `group_by` field is absent, `None`, or
    blank falls into the ungrouped bucket (keyed `None`), which renders without a
    header; that bucket too keeps its first-appearance position.

    Grouping is purely presentational: every record is returned exactly once and
    unchanged, so `value`/`selection`/`options` are unaffected.

    Args:
        records: The normalized option records, in source order.
        group_by: The field name to cluster by, or `None` to skip grouping (the
            whole list is returned as a single ungrouped bucket).

    Returns:
        An ordered list of `(group_label, records)` pairs. `group_label` is the
        group's value coerced to a string, or `None` for the ungrouped bucket.
    """
    if not group_by:
        return [(None, list(records))]
    order: list[str | None] = []
    buckets: dict[str | None, list[OptionRecord]] = {}
    for rec in records:
        raw = record_field(rec, group_by)
        label = None if raw is None or str(raw) == "" else str(raw)
        if label not in buckets:
            buckets[label] = []
            order.append(label)
        buckets[label].append(rec)
    return [(label, buckets[label]) for label in order]


def option_display(record: OptionRecord) -> tuple[Any, bool]:
    """Return the `(icon, disabled)` rendering hints from a record's extras.

    These are the two recognized extra keys that the selection widgets act on:
    `icon` (an icon spec rendered beside the label, or `None`) and `disabled`
    (when truthy the option is shown dimmed and is not user-selectable). Every
    other extra is inert carried data. Each widget maps the pair onto its own
    primitive (`icon=`/`state='disabled'` for the button-backed widgets).

    Args:
        record: The normalized option record.

    Returns:
        A `(icon, disabled)` tuple — `icon` is the spec or `None`; `disabled`
        is a plain `bool`.
    """
    return record.extras.get("icon"), bool(record.extras.get("disabled"))


def option_localize(record: OptionRecord) -> Any:
    """Return a record's per-option `localize` override, or `None` if absent.

    The `localize` key rides in the option's extras (the data bag), like `icon`
    and `disabled`. When present it overrides the widget's group-level
    `localize=` for just this option; `None` means defer to the group setting.

    Args:
        record: The normalized option record.

    Returns:
        The `localize` override (`True`/`False`/`'auto'`), or `None` when the
        option does not carry one.
    """
    return record.extras.get("localize")


def option_is_icon_only(record: OptionRecord) -> bool:
    """Whether an option should render as icon-only (a glyph with no label).

    Inferred — there is no explicit flag: an option is icon-only when it carries
    an `icon` and its `text` is blank. This lets a compact toggle/radio group be
    expressed as `[{'icon': 'list', 'value': 'list'}, ...]` without the caller
    setting `icon_only` per button.

    Args:
        record: The normalized option record.

    Returns:
        `True` when the record has an icon and no (non-whitespace) label.
    """
    icon = record.extras.get("icon")
    return icon is not None and not (record.text or "").strip()