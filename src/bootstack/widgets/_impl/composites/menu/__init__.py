"""Cross-platform menu bar.

A single platform-neutral menu *model* (`MenuModel` / `MenuGroup` / `MenuItem`)
is the source of truth; platform renderers consume it — a themed in-window strip
on Windows/Linux and the native global menu bar on macOS.

See `docs/_dev/menu-redesign.md` for the design.
"""
from __future__ import annotations

from bootstack.widgets._impl.composites.menu.model import (
    MenuGroup,
    MenuItem,
    MenuItemType,
    MenuModel,
)

__all__ = ["MenuModel", "MenuGroup", "MenuItem", "MenuItemType"]