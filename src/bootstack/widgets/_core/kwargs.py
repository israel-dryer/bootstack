"""Merging a caller's options dict over framework-built keyword arguments.

Several widgets accept a bag of options aimed at a widget they build for you —
`Form`'s `editor_options`, `MenuButton`'s `menu_options`, the keyword
passthrough on `ButtonGroup.add` / `RadioGroup.add` / `Toolbar.add_widget`.
Those bags name the built widget's own public keyword arguments, so a caller
may name a parameter the framework also fills.

Splatting both into one call raises `TypeError: got multiple values for
keyword argument`, which names an internal class the caller never wrote.
`merge_kwargs` gives that meeting point one rule instead:

- The caller's options WIN over the framework's defaults. Naming a parameter
  the framework also fills is how you override it.
- A short list of keys is structural — the widget cannot do its job if they
  are replaced (it would be parented elsewhere, or lose the command that emits
  its events). Supplying one raises `BootstackError` naming the API you called
  and what to use instead.
"""
from __future__ import annotations

from typing import Any, Mapping

from bootstack.errors import BootstackError


def reject_reserved(
    user: Mapping[str, Any] | None,
    reserved: Mapping[str, str] | None,
    context: str,
) -> None:
    """Raise if the caller set a key the framework owns.

    Args:
        user: The caller's options. `None` is treated as empty.
        reserved: Structural keys the caller may not set, mapped to the
            guidance shown when they try.
        context: The API the caller invoked, e.g. `'ButtonGroup.add()'`.

    Raises:
        BootstackError: If `user` contains a key listed in `reserved`.
    """
    if not user or not reserved:
        return
    for key in user:
        if key in reserved:
            raise BootstackError(f"{context} does not accept {key}= — {reserved[key]}")


def merge_kwargs(
    defaults: Mapping[str, Any],
    user: Mapping[str, Any] | None,
    *,
    reserved: Mapping[str, str] | None = None,
    context: str = "this call",
) -> dict[str, Any]:
    """Merge a caller's options over framework-built keyword arguments.

    Args:
        defaults: Keyword arguments the framework derived for the call. Any
            key also present in `user` is overridden.
        reserved: Structural keys the caller may not set, mapped to the
            guidance shown when they try.
        context: The API the caller invoked, used in the error message.
        user: The caller's options. `None` is treated as empty.

    Returns:
        The merged keyword arguments.

    Raises:
        BootstackError: If `user` contains a key listed in `reserved`.
    """
    merged = dict(defaults)
    if not user:
        return merged
    reject_reserved(user, reserved, context)
    merged.update(user)
    return merged


# Structural keys a bar's widget-options passthrough may not set — a toolbar or
# status bar places every widget it builds.
RESERVED_BAR_KWARGS = {
    'parent': 'the bar places the widgets it builds.',
}
