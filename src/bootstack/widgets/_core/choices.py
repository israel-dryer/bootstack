"""Construction-time checking for keyword arguments with a closed value set.

Many widget keyword arguments name a behavior mode drawn from a small, closed
set — `selection_mode`, `sorting_mode`, `scrollbars`. The widgets read those
values by comparing against one literal (`mode == 'multi'`), so a near-miss
spelling does not fail: it just takes the other branch. `selection_mode='multiple'`
turns multi-select off and reports nothing, which reads as a broken widget rather
than a typo.

`validate_choice` closes that gap. It runs at construction, names the value it
rejected and the set it accepts, and raises `InvalidChoiceError` — both a
`BootstackError` and a `ValueError`, so either is a valid thing to catch. Call it
before anything else in `__init__`, ahead of parent resolution: a bad value
should be reported as a bad value, not masked by whatever fails next.

Only use it for a genuinely closed set. Arguments that widen their literal with
`| str` — `accent`, `surface` — accept values the alias does not spell out
(`'primary[+1]'`, `'primary[500]'`) and must not be checked this way.
"""
from __future__ import annotations

from typing import Any, Sequence, TypeVar, get_args

from bootstack.errors import InvalidChoiceError
from bootstack.widgets.types import SelectionMode

T = TypeVar("T")

SELECTION_MODES = get_args(SelectionMode)
"""Accepted `selection_mode` values, read from the `SelectionMode` alias so the
check cannot drift from the type."""


def validate_choice(value: T, valid: Sequence[Any], *, param: str, widget: str) -> T:
    """Return `value` if it is in `valid`, otherwise raise.

    Args:
        value: The value the caller supplied.
        valid: The accepted values, in the order they should be listed back.
        param: Name of the keyword argument being checked, e.g.
            `'selection_mode'`.
        widget: Name of the public widget or method the caller used, e.g.
            `'DataTable'`, used to open the message.

    Returns:
        The value, unchanged.

    Raises:
        InvalidChoiceError: If `value` is not in `valid`.
    """
    if value in valid:
        return value
    listed = ", ".join(repr(v) for v in valid)
    raise InvalidChoiceError(
        f"{widget}({param}={value!r}) is not a valid {param}. Valid values: {listed}."
    )