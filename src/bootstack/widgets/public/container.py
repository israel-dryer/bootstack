from __future__ import annotations

import tkinter
from typing import Any

PACK_KEYS = frozenset({
    "side", "fill", "expand", "anchor",
    "padx", "pady", "ipadx", "ipady",
    "before", "after", "in_",
})

GRID_KEYS = frozenset({
    "row", "column", "rowspan", "columnspan",
    "sticky", "padx", "pady", "ipadx", "ipady",
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


# ---  PublicContainer  -------------------------------------------------------
# Imported here (after constants) to avoid circular imports in base.py.

from bootstack.widgets.public.base import PublicWidgetBase  # noqa: E402
from bootstack.widgets.public.context import push_container, pop_container  # noqa: E402


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
