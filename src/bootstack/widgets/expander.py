from __future__ import annotations

import tkinter
from typing import overload, Any, Callable

from bootstack.widgets._impl.composites.expander import Expander as _InternalExpander
from bootstack.widgets._impl.composites.accordion import Accordion as _InternalAccordion
from bootstack.widgets._impl.primitives.packframe import PackFrame
from bootstack.widgets._impl.primitives.gridframe import GridFrame
from bootstack.widgets._core.container import (
    PublicContainer, PACK_KEYS, GRID_KEYS, normalize_fill,
)
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.context import push_container, pop_container
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._core.subscription import Subscription
from bootstack.widgets._core.stream import Stream
from bootstack.widgets.types import Event

_EXPANDER_EVENTS: dict[str, str] = {
    "expand":   "<<Toggle>>",
    "collapse":  "<<Toggle>>",
    "toggle":    "<<Toggle>>",
}


class Expander(PublicContainer):
    """A collapsible container with a clickable header.

    Children placed inside the context block go into the expandable body,
    laid out according to `layout`.

    Args:
        title: Header text.
        layout: Internal layout manager — `'vstack'` (default), `'hstack'`,
            or `'grid'`.
        padding: Space between the expander border and its content.
        gap: Space between children in pixels.
        fill_items: Default fill direction applied to each child.
        expand_items: Whether children expand to fill available space.
        anchor_items: Default anchor applied to each child.
        columns: Column definitions for `'grid'` layout.
        rows: Row definitions for `'grid'` layout.
        sticky_items: Default sticky value for grid children.
        auto_flow: Grid auto-flow direction.
        expanded: If True (default), body is visible on creation.
        collapsible: If False, the header cannot be clicked to collapse.
        show_border: If True, draws a border around the entire expander.
        variant: Header style — `'default'` (ghost/transparent) or `'solid'`.
        icon: Icon displayed in the header.
        icon_position: Where the chevron sits — `'after'` (default) or `'before'`.
        highlight: If True, header shows selected state when expanded.
        accent: Accent token for header styling.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        title: str = "",
        *,
        layout: str = "vstack",
        padding: Any = None,
        gap: int = 0,
        fill_items: str | None = None,
        expand_items: bool | None = None,
        anchor_items: str | None = None,
        columns: int | list | None = None,
        rows: int | list | None = None,
        sticky_items: str | None = None,
        auto_flow: str = "row",
        expanded: bool = True,
        collapsible: bool = True,
        show_border: bool = False,
        variant: str | None = None,
        icon: str | None = None,
        icon_position: str = "after",
        highlight: bool = False,
        accent: str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        self._layout = layout
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "title": title,
            "expanded": expanded,
            "collapsible": collapsible,
            "icon_position": icon_position,
            "highlight": highlight,
        }
        if show_border:
            internal_kwargs["show_border"] = True
        if variant is not None:
            internal_kwargs["variant"] = variant
        if icon is not None:
            internal_kwargs["icon"] = icon
        if accent is not None:
            internal_kwargs["accent"] = accent
        internal_kwargs.update(kwargs)

        self._internal = _InternalExpander(tk_master, **internal_kwargs)

        content = self._internal._content_frame
        if layout in ("vstack", "hstack"):
            self._layout_frame = PackFrame(
                content,
                direction="vertical" if layout == "vstack" else "horizontal",
                padding=padding,
                gap=gap,
                fill_items=normalize_fill(fill_items),
                expand_items=expand_items,
                anchor_items=anchor_items,
            )
        elif layout == "grid":
            self._layout_frame = GridFrame(
                content,
                columns=columns,
                rows=rows,
                padding=padding,
                gap=gap,
                sticky_items=sticky_items,
                auto_flow=auto_flow,
            )
        else:
            raise ValueError(
                f"Expander layout must be 'vstack', 'hstack', or 'grid', got {layout!r}"
            )

        self._fill_items = normalize_fill(fill_items)
        self._expand_items = expand_items
        self._anchor_items = anchor_items
        self._sticky_items = sticky_items
        self._layout_frame.pack(fill="both", expand=True)
        self._attach_to_parent(layout_kw)

    def _child_master(self) -> tkinter.Misc:
        return self._layout_frame

    def _default_layout_method(self) -> str:
        return "grid" if self._layout == "grid" else "pack"

    def _merge_layout_options(self, child: Any, layout_kw: dict) -> tuple[str, dict]:
        if self._layout == "grid":
            options = {k: v for k, v in layout_kw.items() if k in GRID_KEYS}
            if "sticky" not in options and self._sticky_items:
                options["sticky"] = self._sticky_items
            return ("grid", options)
        options = {k: v for k, v in layout_kw.items() if k in PACK_KEYS}
        if "fill" not in options and self._fill_items:
            options["fill"] = self._fill_items
        if "expand" not in options and self._expand_items is not None:
            options["expand"] = self._expand_items
        if "anchor" not in options and self._anchor_items:
            options["anchor"] = self._anchor_items
        return ("pack", options)

    # ----- Properties -----

    @property
    def expanded(self) -> bool:
        return self._internal._expanded

    # ----- Methods -----

    def expand(self) -> None:
        """Expand the body."""
        self._internal.expand()

    def collapse(self) -> None:
        """Collapse the body."""
        self._internal.collapse()

    def toggle(self) -> None:
        """Toggle between expanded and collapsed."""
        self._internal.toggle()

    # ----- Event shorthands -----

    @overload
    def on_toggle(self) -> Stream: ...
    @overload
    def on_toggle(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_toggle(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the expander is expanded or collapsed.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("toggle", handler)


register_widget_events(Expander, _EXPANDER_EVENTS)


class AccordionSection:
    """Context-manager container returned by `Accordion.add()`.

    Accepts the same layout kwargs as `Expander` — `layout=`, `gap=`,
    `fill_items=`, `expand_items=`, `anchor_items=`, `columns=`, `rows=`,
    `sticky_items=`, `auto_flow=`.
    """

    def __init__(
        self,
        internal_expander: _InternalExpander,
        *,
        layout: str = "vstack",
        padding: Any = None,
        gap: int = 0,
        fill_items: str | None = None,
        expand_items: bool | None = None,
        anchor_items: str | None = None,
        columns: int | list | None = None,
        rows: int | list | None = None,
        sticky_items: str | None = None,
        auto_flow: str = "row",
    ) -> None:
        self._expander = internal_expander
        self._layout = layout

        content = internal_expander._content_frame
        if layout in ("vstack", "hstack"):
            self._layout_frame = PackFrame(
                content,
                direction="vertical" if layout == "vstack" else "horizontal",
                padding=padding,
                gap=gap,
                fill_items=normalize_fill(fill_items),
                expand_items=expand_items,
                anchor_items=anchor_items,
            )
        elif layout == "grid":
            self._layout_frame = GridFrame(
                content,
                columns=columns,
                rows=rows,
                padding=padding,
                gap=gap,
                sticky_items=sticky_items,
                auto_flow=auto_flow,
            )
        else:
            raise ValueError(
                f"AccordionSection layout must be 'vstack', 'hstack', or 'grid', got {layout!r}"
            )

        self._fill_items = normalize_fill(fill_items)
        self._expand_items = expand_items
        self._anchor_items = anchor_items
        self._sticky_items = sticky_items
        self._layout_frame.pack(fill="both", expand=True)

    def _child_master(self) -> tkinter.Misc:
        return self._layout_frame

    def guide_layout(self, child: PublicWidgetBase, **layout_kw: Any) -> None:
        if self._layout == "grid":
            options = {k: v for k, v in layout_kw.items() if k in GRID_KEYS}
            if "sticky" not in options and self._sticky_items:
                options["sticky"] = self._sticky_items
            child._internal.grid(in_=self._child_master(), **options)
            return
        options = {k: v for k, v in layout_kw.items() if k in PACK_KEYS}
        if "fill" not in options and self._fill_items:
            options["fill"] = self._fill_items
        if "expand" not in options and self._expand_items is not None:
            options["expand"] = self._expand_items
        if "anchor" not in options and self._anchor_items:
            options["anchor"] = self._anchor_items
        child._internal.pack(in_=self._child_master(), **options)

    def __enter__(self) -> "AccordionSection":
        push_container(self)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pop_container(self)


class Accordion(PublicWidgetBase):
    """A list of collapsible sections, optionally limited to one open at a time.

    Args:
        allow_multiple: If True, multiple sections can be expanded simultaneously.
            Default `False` (only one section open at a time).
        allow_collapse_all: If True, all sections can be collapsed. Default `True`.
        show_separators: If True, draws a separator line between sections.
        show_border: If True, wraps the accordion in a bordered frame.
        variant: Style variant applied to each section header — `'default'`
            (ghost, transparent header) or `'solid'`.
        accent: Accent token for section headers.
        padding: Internal padding around the accordion content.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        *,
        allow_multiple: bool = False,
        allow_collapse_all: bool = True,
        show_separators: bool = False,
        show_border: bool = False,
        variant: str | None = None,
        accent: str | None = None,
        padding: Any = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "allow_multiple": allow_multiple,
            "allow_collapse_all": allow_collapse_all,
            "show_separators": show_separators,
        }
        if show_border:
            internal_kwargs["show_border"] = True
        if variant is not None:
            internal_kwargs["variant"] = variant
        if accent is not None:
            internal_kwargs["accent"] = accent
        if padding is not None:
            internal_kwargs["padding"] = padding
        internal_kwargs.update(kwargs)

        self._internal = _InternalAccordion(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Section management -----

    def remove(self, key: str) -> None:
        """Remove a section by key.

        Args:
            key: The key assigned when the section was added.
        """
        self._internal.remove(key)

    def item(self, key: str) -> Any:
        """Return the internal expander for a section.

        Args:
            key: Section key.
        """
        return self._internal.item(key)

    def items(self, expanded: bool | None = None) -> tuple:
        """Return all section expanders, optionally filtered by expansion state.

        Args:
            expanded: If `True`, return only expanded sections. If `False`,
                only collapsed. If `None` (default), return all.
        """
        return self._internal.items(expanded)

    def keys(self) -> tuple[str, ...]:
        """Return all section keys in insertion order."""
        return self._internal.keys()

    def expand(self, key: str) -> None:
        """Expand the section identified by `key`.

        Args:
            key: Section key.
        """
        self._internal.expand(key)

    def collapse(self, key: str) -> None:
        """Collapse the section identified by `key`.

        Args:
            key: Section key.
        """
        self._internal.collapse(key)

    def expand_all(self) -> None:
        """Expand all sections."""
        self._internal.expand_all()

    def collapse_all(self) -> None:
        """Collapse all sections."""
        self._internal.collapse_all()

    # ----- Events -----

    def on_accordion_changed(self, callback: Callable) -> str:
        """Register a callback for `<<AccordionChange>>` events.

        Args:
            callback: Called when any section expands or collapses.
                `event.data` contains `key`, `title`, and `expanded`.

        Returns:
            Bind ID — pass to `off_accordion_changed()` to unsubscribe.
        """
        return self._internal.on_accordion_changed(callback)

    def off_accordion_changed(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<AccordionChange>>`.

        Args:
            bind_id: ID returned by `on_accordion_changed()`. If `None`, removes all.
        """
        self._internal.off_accordion_changed(bind_id)

    def add(
        self,
        title: str,
        *,
        layout: str = "vstack",
        padding: Any = None,
        gap: int = 0,
        fill_items: str | None = None,
        expand_items: bool | None = None,
        anchor_items: str | None = None,
        columns: int | list | None = None,
        rows: int | list | None = None,
        sticky_items: str | None = None,
        auto_flow: str = "row",
        expanded: bool | None = None,
        icon: str | None = None,
    ) -> AccordionSection:
        """Add a section and return a context manager for placing its children.

        Args:
            title: Section header text.
            layout: Internal layout — `'vstack'` (default), `'hstack'`, or `'grid'`.
            gap: Space between children in pixels.
            fill_items: Default fill direction applied to each child.
            expand_items: Whether children expand to fill available space.
            anchor_items: Default anchor applied to each child.
            columns: Column definitions for `'grid'` layout.
            rows: Row definitions for `'grid'` layout.
            sticky_items: Default sticky value for grid children.
            auto_flow: Grid auto-flow direction.
            expanded: Whether the section starts expanded. Defaults to the
                accordion's own default.
            icon: Icon displayed in the section header.

        Returns:
            `AccordionSection` — use as a context manager to place children.
        """
        exp_kwargs: dict[str, Any] = {}
        if expanded is not None:
            exp_kwargs["expanded"] = expanded
        if icon is not None:
            exp_kwargs["icon"] = icon
        internal_exp = self._internal.add(title=title, **exp_kwargs)
        return AccordionSection(
            internal_exp,
            layout=layout,
            padding=padding,
            gap=gap,
            fill_items=fill_items,
            expand_items=expand_items,
            anchor_items=anchor_items,
            columns=columns,
            rows=rows,
            sticky_items=sticky_items,
            auto_flow=auto_flow,
        )