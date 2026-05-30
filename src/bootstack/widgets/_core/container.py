from __future__ import annotations

import tkinter
from typing import Any

PACK_KEYS = frozenset({
    "side", "fill", "expand", "anchor",
    "padx", "pady", "ipadx", "ipady",
    "margin",
    "before", "after", "in_",
})

GRID_KEYS = frozenset({
    "row", "column", "rowspan", "columnspan",
    "sticky", "padx", "pady", "ipadx", "ipady",
    "margin",
    "in_",
})

PLACE_KEYS = frozenset({
    "x", "y", "relx", "rely",
    "width", "height", "relwidth", "relheight",
    "anchor", "bordermode", "in_",
})

# Presence of any of these signals "use place() instead of pack()/grid()"
PLACE_TRIGGER_KEYS = frozenset({"x", "y", "relx", "rely", "relwidth", "relheight"})

# Human-readable aliases for Tk's single-character fill values.
# Accepted everywhere fill= or fill_items= appears in the public API.
_FILL_ALIASES: dict[str, str] = {
    "horizontal": "x",
    "vertical":   "y",
    "all":        "both",
}


def normalize_fill(value: str | None) -> str | None:
    """Resolve a fill alias to its Tk value, passing through unknowns unchanged."""
    if value is None:
        return None
    return _FILL_ALIASES.get(value, value)


def _expand_margin(layout_kw: dict) -> None:
    """Convert margin= to padx=/pady= in-place. Explicit padx/pady win."""
    margin = layout_kw.pop("margin", None)
    if margin is None:
        return
    if isinstance(margin, int):
        padx = pady = margin
    elif len(margin) == 2:
        padx, pady = margin  # (horizontal, vertical)
    else:
        left, top, right, bottom = margin  # ttk order: left top right bottom
        padx = (left, right)
        pady = (top, bottom)
    layout_kw.setdefault("padx", padx)
    layout_kw.setdefault("pady", pady)


# ---  PublicContainer  -------------------------------------------------------
# Imported here (after constants) to avoid circular imports in base.py.

from bootstack.widgets._core.base import PublicWidgetBase  # noqa: E402
from bootstack.widgets._core.context import push_container, pop_container  # noqa: E402


class PublicContainer(PublicWidgetBase):
    """Base for public containers (HStack, VStack, Grid, App).

    Subclasses must implement `_child_master`, `_default_layout_method`,
    and `_merge_layout_options`.
    """

    def _child_master(self) -> tkinter.Misc:
        """Default: children parent directly to `self._internal`."""
        return self._internal

    def _default_layout_method(self) -> str:
        raise NotImplementedError

    def _merge_layout_options(
        self, child: PublicWidgetBase, layout_kw: dict
    ) -> tuple[str, dict]:
        raise NotImplementedError

    def guide_layout(self, child: PublicWidgetBase, **layout_kw: Any) -> None:
        """Place `child._internal` under this container."""
        if "fill" in layout_kw:
            layout_kw["fill"] = normalize_fill(layout_kw["fill"])
        _expand_margin(layout_kw)
        place_mode = any(k in layout_kw for k in PLACE_TRIGGER_KEYS)
        tk_widget = child._internal

        if place_mode:
            options = {k: v for k, v in layout_kw.items() if k in PLACE_KEYS}
            tk_widget.place(in_=self._child_master(), **options)
            return

        method, options = self._merge_layout_options(child, layout_kw)
        if method == "pack":
            tk_widget.pack(in_=self._child_master(), **options)
        elif method == "grid":
            tk_widget.grid(in_=self._child_master(), **options)
        else:
            raise ValueError(f"Unknown layout method: {method!r}")

    def __enter__(self) -> "PublicContainer":
        push_container(self)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pop_container(self)
        return None
