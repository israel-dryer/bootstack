from __future__ import annotations

from typing import Any, Callable, Literal

from bootstack.widgets.composites.menubar import MenuBar as _InternalMenuBar
from bootstack.widgets.public.base import PublicWidgetBase

Region = Literal["before", "center", "after"]


class MenuBar(PublicWidgetBase):
    """A horizontal menu bar with three layout regions.

    Items are placed into one of three regions: `'before'` (left-aligned),
    `'center'` (stays visually centered), or `'after'` (right-aligned).

    Args:
        gap: Default gap between items in all regions. Default `0`.
        region_gap: Per-region gap override — a dict with keys `'before'`,
            `'center'`, `'after'`, or a 3-tuple `(before, center, after)`.
        chevron: Show a dropdown chevron on menu buttons. Default `False`.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        *,
        gap: int = 0,
        region_gap: dict[str, int] | tuple[int, int, int] | None = None,
        chevron: bool = False,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "gap": gap,
            "chevron": chevron,
        }
        if region_gap is not None:
            internal_kwargs["region_gap"] = region_gap
        internal_kwargs.update(kwargs)

        self._internal = _InternalMenuBar(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Content -----

    def add_button(
        self,
        text: str,
        *,
        region: Region = "before",
        icon: str | None = None,
        on_click: Callable[[], Any] | None = None,
        accent: str | None = None,
        disabled: bool = False,
        **kwargs: Any,
    ) -> None:
        """Add a button to the specified region.

        Args:
            text: Button label text.
            region: Target region — `'before'`, `'center'`, or `'after'`.
            icon: Icon name.
            on_click: Callback fired when clicked.
            accent: Accent token override.
            disabled: If True, button is non-interactive.
        """
        kw: dict[str, Any] = {}
        if icon is not None:
            kw["icon"] = icon
        if on_click is not None:
            kw["command"] = on_click
        if accent is not None:
            kw["accent"] = accent
        if disabled:
            kw["state"] = "disabled"
        kw.update(kwargs)
        self._internal.add_button(text, region=region, **kw)

    def add_label(
        self,
        text: str,
        *,
        region: Region = "before",
        **kwargs: Any,
    ) -> None:
        """Add a text label to the specified region.

        Args:
            text: Label text.
            region: Target region — `'before'`, `'center'`, or `'after'`.
        """
        self._internal.add_label(text, region=region, **kwargs)

    def add_menu(
        self,
        text: str,
        items: list | None = None,
        *,
        region: Region = "before",
        icon: str | None = None,
        accent: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Add a dropdown menu button to the specified region.

        Args:
            text: Menu button label text.
            items: List of `ContextMenuItem` entries for the dropdown.
            region: Target region — `'before'`, `'center'`, or `'after'`.
            icon: Icon name shown on the button.
            accent: Accent token override.
        """
        kw: dict[str, Any] = {}
        if icon is not None:
            kw["icon"] = icon
        if accent is not None:
            kw["accent"] = accent
        kw.update(kwargs)
        self._internal.add_menu(text, items, region=region, **kw)