from __future__ import annotations

import tkinter
from typing import Any

from bootstack.widgets._impl.primitives.panedwindow import PanedWindow as _InternalPanedWindow
from bootstack.widgets._impl.primitives.frame import Frame as _InternalFrame
from bootstack.widgets._impl.primitives.flexframe import FlexFrame
from bootstack.widgets._impl.primitives.gridframe import GridFrame
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.container import (
    GRID_KEYS, grid_sticky, place_flex_child, _reject_legacy_child_kwargs,
    _expand_margin,
)
from bootstack.widgets._core.context import push_container, pop_container
from bootstack.widgets.types import (
    AccentToken, SurfaceToken, Padding, LayoutKind, AutoFlow, Orient,
)


class SplitPane:
    """A handle for one split pane — both a layout context and a live controller.

    Returned by `SplitView.add()` and by `SplitView.item()` / `panes`. Use it as a
    `with` block to place child widgets inside the pane, and read or set `key` /
    `weight` or call `remove()` to inspect, resize, or drop the pane afterward.

    As a context manager it accepts the same layout kwargs as the standalone
    layout containers — `layout=`, `gap=`, `horizontal_items=`, `vertical_items=`,
    `grow_items=`, `columns=`, `rows=`, `auto_flow=`.
    """

    def __init__(
        self,
        frame: tkinter.Widget,
        *,
        key: str,
        paned: _InternalPanedWindow,
        owner: "SplitView",
        layout: LayoutKind = "column",
        padding: Padding | None = None,
        gap: int = 0,
        horizontal_items: str | None = None,
        vertical_items: str | None = None,
        grow_items: bool = False,
        columns: int | list[int | str] | None = None,
        rows: int | list[int | str] | None = None,
        auto_flow: AutoFlow = "row",
    ) -> None:
        self._frame = frame
        self._key = key
        self._paned = paned
        self._owner = owner
        self._layout = layout

        if horizontal_items is None:
            horizontal_items = (
                "stretch" if layout == "grid"
                else "center" if layout == "column" else "left"
            )
        if vertical_items is None:
            vertical_items = (
                "stretch" if layout == "grid"
                else "center" if layout == "row" else "top"
            )

        if layout in ("column", "row"):
            self._layout_frame = FlexFrame(
                frame,
                direction="vertical" if layout == "column" else "horizontal",
                padding=padding,
                gap=gap,
                horizontal_items=horizontal_items,
                vertical_items=vertical_items,
                grow_items=grow_items,
            )
        elif layout == "grid":
            self._layout_frame = GridFrame(
                frame,
                columns=columns,
                rows=rows,
                padding=padding,
                gap=gap,
                auto_flow=auto_flow,
            )
        else:
            raise ValueError(
                f"SplitPane layout must be 'column', 'row', or 'grid', got {layout!r}"
            )

        self._horizontal_items = horizontal_items
        self._vertical_items = vertical_items
        self._layout_frame.pack(fill="both", expand=True)

    def _child_master(self) -> tkinter.Widget:
        return self._layout_frame

    def guide_layout(self, child: PublicWidgetBase, **layout_kw: Any) -> None:
        if self._layout == "grid":
            _reject_legacy_child_kwargs(layout_kw, "SplitPane")
            _expand_margin(layout_kw)
            options = {k: v for k, v in layout_kw.items() if k in GRID_KEYS}
            h = layout_kw.get("horizontal") or self._horizontal_items
            v = layout_kw.get("vertical") or self._vertical_items
            options["sticky"] = grid_sticky(h, v)
            child._internal.grid(in_=self._child_master(), **options)
            return
        place_flex_child(self._layout_frame, child, layout_kw, "SplitPane")

    # ----- Pane identity, weight, and removal -----

    @property
    def key(self) -> str:
        """The pane's unique key, used with `SplitView.item()` / `remove()`."""
        return self._key

    @property
    def weight(self) -> int:
        """Relative resize weight — panes with a higher weight take proportionally
        more space when the container grows. A pane with `weight=0` keeps its size
        and does not grow (a fixed pane). Assigning a new value resizes live.
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
    look one up with `item()`, place a new one next to another with
    `add(before=)` / `add(after=)`, reorder with `move()`, and drop one with
    `remove()`.

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
        key: str | None = None,
        *,
        before: str | None = None,
        after: str | None = None,
        weight: int = 1,
        layout: LayoutKind = "column",
        padding: Padding | None = None,
        gap: int = 0,
        horizontal_items: str | None = None,
        vertical_items: str | None = None,
        grow_items: bool = False,
        columns: int | list[int | str] | None = None,
        rows: int | list[int | str] | None = None,
        auto_flow: AutoFlow = "row",
    ) -> SplitPane:
        """Add a pane and return a handle for placing its children and controlling it.

        Panes are appended in order by default. Pass `before=` or `after=` (the
        key of an existing pane) to place the new pane next to another one.

        Args:
            key: Unique identifier for the pane, used with `item()`, `move()`,
                and `remove()`. Auto-generated when omitted.
            before: Place the new pane immediately before the pane with this key.
            after: Place the new pane immediately after the pane with this key.
                Mutually exclusive with `before`; omit both to append at the end.
            weight: Relative size weight when the container is resized. Panes
                with a higher weight take proportionally more space. Settable
                afterward via the pane's `weight` property. Defaults to `1`.
            layout: Internal pane layout. Defaults to `'column'`.
            padding: Space in pixels inside the pane border. Defaults to `None`.
            gap: Space in pixels between children. Defaults to `0`.
            horizontal_items: How children sit on the horizontal axis — edge
                values `'left'`/`'center'`/`'right'`/`'stretch'`, plus `'space-*'`
                when horizontal is the stacking axis. Defaults to `'stretch'` in grid mode,
                `'center'` in a column and `'left'` in a row.
            vertical_items: How children sit on the vertical axis — edge values
                `'top'`/`'center'`/`'bottom'`/`'stretch'`, plus `'space-*'` when
                vertical is the stacking axis. Defaults to `'stretch'` in grid mode,
                `'center'` in a row and `'top'` in a column.
            grow_items: For `'column'`/`'row'`, when `True` every child grows
                equally to share the main axis. Defaults to `False`.
            columns: Column definitions for `'grid'` layout. An integer sets
                the number of equal-weight columns; a list sets per-column
                weights or sizes (e.g. `[1, 2, 'auto', '120px']`).
            rows: Row definitions for `'grid'` layout, same format as `columns`.
            auto_flow: Grid auto-flow direction. Defaults to `'row'`.

        Returns:
            `SplitPane` — use as a context manager to place children, and as a
            handle to read/set `weight` or `remove()` the pane.

        Raises:
            KeyError: If `before`/`after` names a pane that does not exist.
            ValueError: If both `before` and `after` are given.
        """
        index = self._resolve_placement(before, after)
        return self._create_pane(
            index=index, key=key, weight=weight,
            layout=layout, padding=padding, gap=gap,
            horizontal_items=horizontal_items, vertical_items=vertical_items,
            grow_items=grow_items,
            columns=columns, rows=rows, auto_flow=auto_flow,
        )

    def move(self, key: str, *, before: str | None = None, after: str | None = None) -> None:
        """Move an existing pane next to another pane.

        Args:
            key: The key of the pane to move.
            before: Move it immediately before the pane with this key.
            after: Move it immediately after the pane with this key. Pass
                exactly one of `before` or `after`.

        Raises:
            KeyError: If `key`, `before`, or `after` names a pane that does
                not exist.
            ValueError: If not exactly one of `before`/`after` is given, or if
                the anchor is the pane being moved.
        """
        if key not in self._panes:
            raise KeyError(f"no pane with key {key!r}")
        if (before is None) == (after is None):
            raise ValueError("pass exactly one of before= or after=")
        anchor = before if before is not None else after
        if anchor == key:
            raise ValueError(f"cannot move pane {key!r} relative to itself")
        # The target index is computed against the order with the moved pane
        # removed, which is how ttk's insert(pos, existing) re-seats it.
        order = [k for k in self._panes if k != key]
        if anchor not in order:
            raise KeyError(f"no pane with key {anchor!r}")
        pos = order.index(anchor)
        index = pos if before is not None else pos + 1
        self._internal.insert(index, self._panes[key]._frame)
        self._resync_order()

    def _resolve_placement(self, before: str | None, after: str | None) -> int | None:
        """Translate a `before=`/`after=` key into an insertion index for a new pane.

        Returns `None` to append (the default, and the case where the anchor is
        the last pane — ttk cannot target the slot past the final pane).
        """
        if before is not None and after is not None:
            raise ValueError("pass only one of before= or after=, not both")
        if before is None and after is None:
            return None
        anchor = before if before is not None else after
        order = list(self._panes)
        if anchor not in order:
            raise KeyError(f"no pane with key {anchor!r}")
        pos = order.index(anchor)
        index = pos if before is not None else pos + 1
        return index if index < len(order) else None

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
        self._internal.tk.call(str(self._internal), "forget", pane._frame)
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
            index: Zero-based sash index. A split view with `n` panes has
                `n - 1` sashes.
            position: New position in pixels. If `None`, returns the
                current position.

        Returns:
            Current sash position in pixels when `position` is `None`.

        Raises:
            IndexError: If `index` does not refer to an existing sash.
        """
        n_sashes = max(0, len(self._internal.panes()) - 1)
        if not 0 <= index < n_sashes:
            if n_sashes == 0:
                raise IndexError(
                    f"sash index {index} out of range: this split view has no "
                    f"sashes yet (add at least two panes)"
                )
            raise IndexError(
                f"sash index {index} out of range: valid sash indices are "
                f"0..{n_sashes - 1}"
            )
        if position is None:
            return self._internal.sashpos(index)
        self._internal.sashpos(index, position)
        return None
