from __future__ import annotations

import tkinter
from typing import Any

from bootstack.widgets._impl.primitives.panedwindow import PanedWindow as _InternalPanedWindow
from bootstack.widgets._impl.primitives.frame import Frame as _InternalFrame
from bootstack.widgets._impl.primitives.packframe import PackFrame
from bootstack.widgets._impl.primitives.gridframe import GridFrame
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.container import PACK_KEYS, GRID_KEYS, normalize_fill
from bootstack.widgets._core.context import push_container, pop_container
from bootstack.widgets.types import (
    AccentToken, SurfaceToken, Fill, Anchor, Sticky, Padding, LayoutKind, AutoFlow,
    Orient,
)


class SplitPane:
    """A handle for one split pane — both a layout context and a live controller.

    Returned by `SplitView.add()` and by `SplitView.item()` / `panes`. Use it as a
    `with` block to place child widgets inside the pane, and read or set `key` /
    `weight` or call `remove()` to inspect, resize, or drop the pane afterward.

    As a context manager it accepts the same layout kwargs as the standalone
    layout containers — `layout=`, `gap=`, `fill_items=`, `expand_items=`,
    `anchor_items=`, `columns=`, `rows=`, `sticky_items=`, `auto_flow=`.
    """

    def __init__(
        self,
        frame: tkinter.Widget,
        *,
        key: str,
        paned: _InternalPanedWindow,
        owner: "SplitView",
        layout: LayoutKind = "vstack",
        padding: Padding | None = None,
        gap: int = 0,
        fill_items: Fill | str | None = None,
        expand_items: bool | None = None,
        anchor_items: Anchor | str | None = None,
        columns: int | list[int | str] | None = None,
        rows: int | list[int | str] | None = None,
        sticky_items: Sticky | str | None = None,
        auto_flow: AutoFlow = "row",
    ) -> None:
        self._frame = frame
        self._key = key
        self._paned = paned
        self._owner = owner
        self._layout = layout

        if layout in ("vstack", "hstack"):
            self._layout_frame = PackFrame(
                frame,
                direction="vertical" if layout == "vstack" else "horizontal",
                padding=padding,
                gap=gap,
                fill_items=normalize_fill(fill_items),
                expand_items=expand_items,
                anchor_items=anchor_items,
            )
        elif layout == "grid":
            self._layout_frame = GridFrame(
                frame,
                columns=columns,
                rows=rows,
                padding=padding,
                gap=gap,
                sticky_items=sticky_items,
                auto_flow=auto_flow,
            )
        else:
            raise ValueError(
                f"SplitPane layout must be 'vstack', 'hstack', or 'grid', got {layout!r}"
            )

        self._fill_items = normalize_fill(fill_items)
        self._expand_items = expand_items
        self._anchor_items = anchor_items
        self._sticky_items = sticky_items
        self._layout_frame.pack(fill="both", expand=True)

    def _child_master(self) -> tkinter.Widget:
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

    # ----- Pane identity, weight, and removal -----

    @property
    def key(self) -> str:
        """The pane's unique key, used with `SplitView.item()` / `remove()`."""
        return self._key

    @property
    def weight(self) -> int:
        """Relative resize weight — panes with a higher weight take proportionally
        more space when the container grows. Assigning a new value resizes live.
        """
        return int(self._paned.pane(self._frame, "weight"))

    @weight.setter
    def weight(self, value: int) -> None:
        self._paned.pane(self._frame, weight=value)

    def remove(self) -> None:
        """Remove this pane and its content from the split view."""
        self._owner.remove(self._key)

    def __enter__(self) -> "SplitPane":
        push_container(self)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pop_container(self)


class SplitView(PublicWidgetBase):
    """A resizable split container with panes separated by draggable sashes.

    Add panes with `.add()` and place children inside each pane using the
    returned `SplitPane` handle. Sashes between panes can be dragged at runtime
    to resize them. Panes are addressable by key — enumerate them with `panes`,
    look one up with `item()`, insert one at a position with `insert()`, reorder
    with `move()`, and drop one with `remove()`.

    Args:
        orient: Pane arrangement — `'horizontal'` (side-by-side) or
            `'vertical'` (stacked top-to-bottom). Defaults to `'horizontal'`.
        padding: Space in pixels between the outer border and the pane area.
            A single value applies to all sides; `(x, y)` sets the horizontal
            and vertical amounts. Defaults to `None`.
        accent: Color intent token applied to the sash. When omitted, the
            sash uses the theme's default color.
        surface: Surface token for the pane background.
        sash_thickness: Width (horizontal split) or height (vertical split)
            of the draggable sash in pixels. Defaults to the theme's
            standard sash size (typically 6 px).
        width: Requested width in pixels.
        height: Requested height in pixels.
        parent: Override the context-stack parent.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        orient: Orient = "horizontal",
        *,
        padding: Padding | None = None,
        accent: AccentToken | str | None = None,
        surface: SurfaceToken | str | None = None,
        sash_thickness: int | None = None,
        width: int | None = None,
        height: int | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        pw_kwargs: dict[str, Any] = {"orient": orient}
        if padding is not None:
            pw_kwargs["padding"] = padding
        if accent is not None:
            pw_kwargs["accent"] = accent
        if surface is not None:
            pw_kwargs["surface"] = surface
        if width is not None:
            pw_kwargs["width"] = width
        if height is not None:
            pw_kwargs["height"] = height
        if sash_thickness is not None:
            pw_kwargs["style_options"] = {"sash_thickness": sash_thickness}

        self._panes: dict[str, SplitPane] = {}
        self._pane_counter = 0

        tk_master = self._parent._child_master() if self._parent else None
        self._internal = _InternalPanedWindow(tk_master, **pw_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Pane management -----

    def add(
        self,
        *,
        key: str | None = None,
        weight: int = 1,
        layout: LayoutKind = "vstack",
        padding: Padding | None = None,
        gap: int = 0,
        fill_items: Fill | str | None = None,
        expand_items: bool | None = None,
        anchor_items: Anchor | str | None = None,
        columns: int | list[int | str] | None = None,
        rows: int | list[int | str] | None = None,
        sticky_items: Sticky | str | None = None,
        auto_flow: AutoFlow = "row",
    ) -> SplitPane:
        """Add a pane and return a handle for placing its children and controlling it.

        Args:
            key: Unique identifier used with `item()` and `remove()`.
                Auto-generated if omitted.
            weight: Relative size weight when the container is resized. Panes
                with a higher weight take proportionally more space. Settable
                afterward via the pane's `weight` property. Defaults to `1`.
            layout: Internal pane layout. Defaults to `'vstack'`.
            padding: Space in pixels inside the pane border. Defaults to `None`.
            gap: Space in pixels between children. Defaults to `0`.
            fill_items: Default fill direction applied to every child.
            expand_items: Whether children expand to consume extra space.
            anchor_items: Default anchor applied to every child.
            columns: Column definitions for `'grid'` layout. An integer sets
                the number of equal-weight columns; a list sets per-column
                weights or sizes (e.g. `[1, 2, 'auto', '120px']`).
            rows: Row definitions for `'grid'` layout, same format as `columns`.
            sticky_items: Default sticky value for grid children.
            auto_flow: Grid auto-flow direction. Defaults to `'row'`.

        Returns:
            `SplitPane` — use as a context manager to place children, and as a
            handle to read/set `weight` or `remove()` the pane.
        """
        return self._create_pane(
            index=None, key=key, weight=weight,
            layout=layout, padding=padding, gap=gap, fill_items=fill_items,
            expand_items=expand_items, anchor_items=anchor_items,
            columns=columns, rows=rows, sticky_items=sticky_items,
            auto_flow=auto_flow,
        )

    def insert(
        self,
        index: int,
        *,
        key: str | None = None,
        weight: int = 1,
        layout: LayoutKind = "vstack",
        padding: Padding | None = None,
        gap: int = 0,
        fill_items: Fill | str | None = None,
        expand_items: bool | None = None,
        anchor_items: Anchor | str | None = None,
        columns: int | list[int | str] | None = None,
        rows: int | list[int | str] | None = None,
        sticky_items: Sticky | str | None = None,
        auto_flow: AutoFlow = "row",
    ) -> SplitPane:
        """Add a pane at a specific position. Accepts the same options as `add()`.

        Args:
            index: Zero-based position to insert the new pane at. Existing panes
                at or after this position shift toward the end.
            key: Unique identifier used with `item()` and `remove()`.
                Auto-generated if omitted.
            weight: Relative size weight. Defaults to `1`.
            layout: Internal pane layout. Defaults to `'vstack'`.
            padding: Space in pixels inside the pane border. Defaults to `None`.
            gap: Space in pixels between children. Defaults to `0`.
            fill_items: Default fill direction applied to every child.
            expand_items: Whether children expand to consume extra space.
            anchor_items: Default anchor applied to every child.
            columns: Column definitions for `'grid'` layout.
            rows: Row definitions for `'grid'` layout.
            sticky_items: Default sticky value for grid children.
            auto_flow: Grid auto-flow direction. Defaults to `'row'`.

        Returns:
            `SplitPane` — same handle returned by `add()`.
        """
        return self._create_pane(
            index=index, key=key, weight=weight,
            layout=layout, padding=padding, gap=gap, fill_items=fill_items,
            expand_items=expand_items, anchor_items=anchor_items,
            columns=columns, rows=rows, sticky_items=sticky_items,
            auto_flow=auto_flow,
        )

    def move(self, key: str, index: int) -> None:
        """Move an existing pane to a new position.

        Args:
            key: The key of the pane to move.
            index: Zero-based target position.
        """
        pane = self._panes[key]
        self._internal.insert(index, pane._frame)
        self._resync_order()

    def _create_pane(self, *, index: int | None, key: str | None, weight: int, **layout_kw: Any) -> SplitPane:
        if key is None:
            key = f"pane_{self._pane_counter}"
            self._pane_counter += 1
        if key in self._panes:
            raise ValueError(f"A pane with the key {key!r} already exists.")

        frame = _InternalFrame(self._internal)
        if index is None:
            self._internal.add(frame, weight=weight)
        else:
            self._internal.insert(index, frame, weight=weight)
        pane = SplitPane(frame, key=key, paned=self._internal, owner=self, **layout_kw)
        self._panes[key] = pane
        if index is not None:
            self._resync_order()
        return pane

    def _resync_order(self) -> None:
        """Reorder `_panes` to match the live pane order after an insert/move."""
        by_frame = {str(p._frame): (k, p) for k, p in self._panes.items()}
        self._panes = dict(
            by_frame[fid] for fid in self._internal.panes() if fid in by_frame
        )

    @property
    def panes(self) -> tuple[SplitPane, ...]:
        """All panes in left-to-right (or top-to-bottom) order."""
        return tuple(self._panes.values())

    def __len__(self) -> int:
        return len(self._panes)

    def keys(self) -> tuple[str, ...]:
        """All pane keys in order."""
        return tuple(self._panes)

    def item(self, key: str) -> SplitPane:
        """Return the pane handle for `key`.

        Args:
            key: Pane key.

        Returns:
            The `SplitPane` for that key — read/set its `weight` or `remove()` it.
        """
        return self._panes[key]

    def remove(self, key: str) -> None:
        """Remove a pane and destroy its content.

        Args:
            key: The key assigned when the pane was added.
        """
        pane = self._panes.pop(key)
        # `WidgetCapabilitiesMixin.forget()` shadows `ttk.Panedwindow.forget(pane)`
        # with a zero-arg method, so invoke the underlying Tk command directly.
        self._internal.tk.call(self._internal._w, "forget", pane._frame)
        pane._frame.destroy()

    # ----- Sash control -----

    @property
    def sash_positions(self) -> list[int]:
        """Current position of every sash in pixels, in order."""
        n = len(self._internal.panes())
        return [self._internal.sashpos(i) for i in range(max(0, n - 1))]

    def sash_position(self, index: int, position: int | None = None) -> int | None:
        """Get or set the position of a sash.

        Args:
            index: Zero-based sash index.
            position: New position in pixels. If `None`, returns the
                current position.

        Returns:
            Current sash position in pixels when `position` is `None`.
        """
        if position is None:
            return self._internal.sashpos(index)
        self._internal.sashpos(index, position)
        return None
