"""Public font configuration for bootstack.

These functions adjust the application's typography at runtime. They operate on
the framework's font tokens (`body`, `code`, `heading-lg`, …); see the
typography reference for the full token list.

Call them inside an active app (within `with bs.App():`), since fonts are bound
to the application's Tk interpreter.
"""
from __future__ import annotations

import warnings
from tkinter import font as tkfont
from typing import Literal

from bootstack.style.typography import Typography

__all__ = ["get_font_families", "set_font_family", "update_font_token"]


def _installed_families() -> set[str]:
    """Raw set of font families known to the active Tk interpreter."""
    return set(tkfont.families())


def get_font_families() -> list[str]:
    """Return the installed UI font families available to the application.

    System fonts that start with `@` and emoji fonts are filtered out, leaving
    the families suitable for body and heading text. The list is sorted
    alphabetically.

    Returns:
        Sorted list of font family names.
    """
    families = {
        f for f in _installed_families()
        if f and not f.startswith("@") and "emoji" not in f.lower()
    }
    return sorted(families)


def set_font_family(family: str, *, mono_family: str | None = None) -> None:
    """Set the application font family for all non-code text.

    Every token except `code` is switched to `family`; the monospace `code`
    token is left untouched unless `mono_family` is given. If a requested
    family is not installed, a warning is issued and the current fonts are left
    unchanged.

    Args:
        family: Font family for body, heading, label, and caption text
            (e.g. `'Segoe UI'`, `'Inter'`). Must be installed.
        mono_family: Optional family for the `code` token. Defaults to leaving
            the existing monospace family in place.
    """
    installed = _installed_families()
    if family not in installed:
        warnings.warn(
            f"Font family {family!r} is not installed; fonts left unchanged. "
            f"Use get_font_families() to list available families.",
            stacklevel=2,
        )
        return
    if mono_family is not None and mono_family not in installed:
        warnings.warn(
            f"Font family {mono_family!r} is not installed; fonts left unchanged. "
            f"Use get_font_families() to list available families.",
            stacklevel=2,
        )
        return
    Typography.set_global_family(family, mono_family=mono_family)


def update_font_token(
    name: str,
    *,
    family: str | None = None,
    size: int | None = None,
    weight: Literal["normal", "bold"] | None = None,
    slant: Literal["roman", "italic"] | None = None,
    underline: bool | None = None,
    overstrike: bool | None = None,
) -> None:
    """Override the attributes of a single font token.

    Only the attributes you pass are changed; the rest of the token is left as
    is. The update applies everywhere the token is used.

    Args:
        name: Token to update (e.g. `'body'`, `'heading-lg'`, `'code'`).
        family: New font family. Must be installed.
        size: New point size.
        weight: `'normal'` or `'bold'`.
        slant: `'roman'` or `'italic'`.
        underline: Whether to underline the text.
        overstrike: Whether to strike through the text.
    """
    if name not in Typography.token_names():
        raise ValueError(
            f"Unknown font token: {name!r}. "
            f"Valid tokens: {', '.join(sorted(Typography.token_names()))}."
        )
    if family is not None and family not in _installed_families():
        warnings.warn(
            f"Font family {family!r} is not installed; token left unchanged. "
            f"Use get_font_families() to list available families.",
            stacklevel=2,
        )
        return

    changes = {
        "font": family,
        "size": size,
        "weight": weight,
        "slant": slant,
        "underline": underline,
        "overstrike": overstrike,
    }
    changes = {k: v for k, v in changes.items() if v is not None}
    if not changes:
        return
    Typography.update_font_token(name, **changes)
