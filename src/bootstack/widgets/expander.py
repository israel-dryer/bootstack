from __future__ import annotations

import tkinter
from typing import overload, Any, Callable, Literal

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
from bootstack.events import AccordionChangeEvent, Subscription, ToggleEvent
from bootstack.streams import Stream
from bootstack.widgets.types import (
    Event, AccentToken, Fill, Anchor, Sticky, Padding, LayoutKind, AutoFlow,
)

# Accordion/Expander headers register only the `'solid'` and `'default'` builders
# (`style/builders/expander.py`); the default reads as a ghost/transparent header.
AccordionVariant = Literal['solid', 'default']

_EXPANDER_EVENTS: dict[str, str] = {
    "expand":   "<<Toggle>>",
    "collapse":  "<<Toggle>>",
    "toggle":    "<<Toggle>>",
}

_ACCORDION_EVENTS: dict[str, str] = {
    "change": "<<AccordionChange>>",
}


class Expander(PublicContainer):
    """A collapsible container with a clickable header.

    Children placed inside the context block go into the expandable body,
    laid out according to `layout`.

    Args:
        title: Header text shown in the clickable header bar.
        layout: Internal layout for the body. One of ``'vstack'`` (default),
            ``'hstack'``, or ``'grid'``.
        padding: Space between the expander border and its body content, in
            pixels. Accepts a single int or a ``(x, y)`` tuple.
        gap: Space between body children in pixels. Default ``0``.
        fill_items: Default fill direction applied to each body child.
            One of ``'none'``, ``'x'``, ``'y'``, ``'both'``. Default ``None``
            (no fill applied).
        expand_items: If ``True``, body children receive extra space along the
            pack direction. Default ``None`` (not applied).
        anchor_items: Default anchor applied to each body child. One of
            ``'n'``, ``'ne'``, ``'e'``, ``'se'``, ``'s'``, ``'sw'``,
            ``'w'``, ``'nw'``, ``'center'``. Default ``None``.
        columns: Column size definitions for ``'grid'`` layout. An integer
            creates that many equal-weight columns; a list of ints sets
            per-column weights. Default ``None``.
        rows: Row size definitions for ``'grid'`` layout. Same format as
            ``columns``. Default ``None``.
        sticky_items: Default cell alignment for grid children. Any combination
            of ``'n'``, ``'s'``, ``'e'``, ``'w'``. Default ``None``.
        auto_flow: Grid placement direction — ``'row'`` (default) or
            ``'column'``.
        expanded: If ``True`` (default), the body is visible on creation.
        collapsible: If ``True`` (default), clicking the header toggles the
            body. If ``False``, the chevron is hidden and the body stays open.
        show_border: If ``True``, draws a border around the entire widget.
            Default ``False``.
        variant: Header style. Defaults to `None` (the default header reads
            as a ghost/transparent bar).
        icon: Icon name or spec displayed to the left of the title.
        icon_position: Side on which the collapse chevron appears —
            ``'after'`` (default, right of title) or ``'before'`` (left).
        highlight: If ``True``, the header shows a selected visual state while
            the body is expanded. Default ``False``.
        accent: Color intent token for the header. Defaults to `None`
            (theme default).
        parent: Explicit parent container. Omit to use the current context.
    """

    def __init__(
        self,
        title: str = "",
        *,
        layout: LayoutKind = "vstack",
        padding: Padding | None = None,
        gap: int = 0,
        fill_items: Fill | None = None,
        expand_items: bool | None = None,
        anchor_items: Anchor | None = None,
        columns: int | list[int | str] | None = None,
        rows: int | list[int | str] | None = None,
        sticky_items: Sticky | None = None,
        auto_flow: AutoFlow = "row",
        expanded: bool = True,
        collapsible: bool = True,
        show_border: bool = False,
        variant: AccordionVariant | None = None,
        icon: str | None = None,
        icon_position: Literal["before", "after"] = "after",
        highlight: bool = False,
        accent: AccentToken | str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        self._layout = layout
        layout_kw = self._split_layout_kwargs(kwargs)
        layout_kw.setdefault("fill", "x")

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
    def on_toggle(self, handler: Callable[[ToggleEvent], Any]) -> Subscription: ...
    def on_toggle(self, handler: Callable[[ToggleEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the expander is expanded or collapsed.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("toggle", handler)


register_widget_events(Expander, _EXPANDER_EVENTS)


class AccordionSection:
    """A handle for one accordion section — both a layout context and a live controller.

    Returned by `Accordion.add()` and by `Accordion.item()` / `items()`. Use it
    as a `with` block to place child widgets inside the section, and read or call
    `key` / `title` / `expanded` / `expand()` / `collapse()` / `toggle()` to
    inspect or drive the section afterward.

    As a context manager it accepts the same layout kwargs as the standalone
    layout containers — `layout=`, `gap=`, `fill_items=`, `expand_items=`,
    `anchor_items=`, `columns=`, `rows=`, `sticky_items=`, `auto_flow=`.
    """

    def __init__(
        self,
        internal_expander: _InternalExpander,
        *,
        key: str,
        layout: LayoutKind = "vstack",
        padding: Padding | None = None,
        gap: int = 0,
        fill_items: Fill | None = None,
        expand_items: bool | None = None,
        anchor_items: Anchor | None = None,
        columns: int | list[int | str] | None = None,
        rows: int | list[int | str] | None = None,
        sticky_items: Sticky | None = None,
        auto_flow: AutoFlow = "row",
    ) -> None:
        self._expander = internal_expander
        self._key = key
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

    # ----- Section identity, state, and control -----

    @property
    def key(self) -> str:
        """The section's unique key, used with `Accordion.item()`/`remove()`."""
        return self._key

    @property
    def title(self) -> str:
        """The section header text. Assigning a new value relabels the header."""
        return self._expander._title

    @title.setter
    def title(self, value: str) -> None:
        self._expander.configure(title=value)

    @property
    def expanded(self) -> bool:
        """Whether the section is currently expanded."""
        return self._expander._expanded

    def expand(self) -> None:
        """Expand this section."""
        self._expander.expand()

    def collapse(self) -> None:
        """Collapse this section."""
        self._expander.collapse()

    def toggle(self) -> None:
        """Toggle this section between expanded and collapsed."""
        self._expander.toggle()

    def __enter__(self) -> "AccordionSection":
        push_container(self)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pop_container(self)


class Accordion(PublicWidgetBase):
    """A list of collapsible sections, optionally limited to one open at a time.

    Each section is added with `add()`, which returns an `AccordionSection`
    context manager for placing child widgets inside that section.

    Args:
        allow_multiple: If `True`, multiple sections can be expanded at
            once. Defaults to `False` (only one section open at a time).
        allow_collapse_all: If `True` (default), every section can be
            collapsed. If `False`, at least one section stays open.
        show_separators: If `True`, draws a separator line between sections.
            Defaults to `True`.
        show_border: If `True`, wraps the accordion in a bordered frame.
            Defaults to `True`.
        variant: Style variant applied to each section header. Defaults to
            `None` (the default header reads as a ghost/transparent bar).
        accent: Color intent token applied to all section headers. Defaults
            to `None` (theme default).
        padding: Space between the outer border and the sections, in pixels.
            Defaults to `None`.
        parent: Explicit parent container. Omit to use the current context.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        *,
        allow_multiple: bool = False,
        allow_collapse_all: bool = True,
        show_separators: bool = True,
        show_border: bool = True,
        variant: AccordionVariant | None = None,
        accent: AccentToken | str | None = None,
        padding: Padding | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        layout_kw.setdefault("fill", "x")

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

        self._sections: dict[str, AccordionSection] = {}
        self._internal = _InternalAccordion(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Section management -----

    def remove(self, key: str) -> None:
        """Remove a section by key.

        Args:
            key: The key assigned when the section was added.
        """
        self._internal.remove(key)
        self._sections.pop(key, None)

    def item(self, key: str) -> AccordionSection:
        """Return the section handle for `key`.

        Args:
            key: Section key.

        Returns:
            The `AccordionSection` for that key — read `expanded`/`title` or call
            `expand()`/`collapse()`/`toggle()` to drive it.
        """
        return self._sections[key]

    def items(self, expanded: bool | None = None) -> tuple[AccordionSection, ...]:
        """Return all section handles in insertion order, optionally filtered.

        Args:
            expanded: If `True`, return only expanded sections. If `False`,
                only collapsed. If `None` (default), return all.

        Returns:
            A tuple of `AccordionSection` handles.
        """
        sections = (self._sections[k] for k in self._internal.keys())
        if expanded is None:
            return tuple(sections)
        return tuple(s for s in sections if s.expanded == expanded)

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

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[AccordionChangeEvent], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[AccordionChangeEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when any section expands or collapses.

        The handler receives an `AccordionChangeEvent`; ``e.expanded`` is the
        tuple of currently expanded sections.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("change", handler)

    def add(
        self,
        title: str,
        *,
        key: str | None = None,
        layout: LayoutKind = "vstack",
        padding: Padding | None = 16,
        gap: int = 0,
        fill_items: Fill | None = None,
        expand_items: bool | None = None,
        anchor_items: Anchor | None = None,
        columns: int | list[int | str] | None = None,
        rows: int | list[int | str] | None = None,
        sticky_items: Sticky | None = None,
        auto_flow: AutoFlow = "row",
        expanded: bool | None = None,
        icon: str | None = None,
    ) -> AccordionSection:
        """Add a section and return a context manager for placing its children.

        Args:
            title: Section header text.
            key: Unique identifier used with `item()`, `expand()`, `collapse()`,
                and `remove()`. Auto-generated if omitted.
            layout: Body layout. Defaults to `'vstack'`.
            padding: Space between the section border and its body, in pixels.
                Defaults to `16`.
            gap: Space between body children in pixels. Defaults to `0`.
            fill_items: Default fill direction for body children. Defaults to
                `None`.
            expand_items: If `True`, body children expand along the pack
                direction. Defaults to `None`.
            anchor_items: Default anchor for body children. Defaults to `None`.
            columns: Column definitions for `'grid'` layout. An integer sets
                the number of equal-weight columns; a list sets per-column
                weights or sizes (e.g. `[1, 2, 'auto', '120px']`).
                Defaults to `None`.
            rows: Row definitions for `'grid'` layout. Defaults to `None`.
            sticky_items: Default cell alignment for grid children.
                Defaults to `None`.
            auto_flow: Grid placement direction. Defaults to `'row'`.
            expanded: Whether the section starts expanded. Defaults to the
                accordion's own default (collapsed when `allow_multiple=False`).
            icon: Icon name or spec displayed in the section header.

        Returns:
            `AccordionSection` — use as a context manager to place children.
        """
        exp_kwargs: dict[str, Any] = {}
        if key is not None:
            exp_kwargs["key"] = key
        if expanded is not None:
            exp_kwargs["expanded"] = expanded
        if icon is not None:
            exp_kwargs["icon"] = icon
        internal_exp = self._internal.add(title=title, **exp_kwargs)
        # The internal accordion auto-generates a key when one is not supplied;
        # recover the resolved key so the section handle can be looked up later.
        resolved_key = next(
            k for k, v in self._internal._expanders.items() if v is internal_exp
        )
        section = AccordionSection(
            internal_exp,
            key=resolved_key,
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
        self._sections[resolved_key] = section
        return section


register_widget_events(Accordion, _ACCORDION_EVENTS)