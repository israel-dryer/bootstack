from __future__ import annotations

import tkinter as tk
from typing import Any

from typing_extensions import Unpack

from bootstack.widgets._impl.primitives.frame import Frame, FrameKwargs
from bootstack.widgets._impl.mixins.configure_mixin import configure_delegate
from bootstack.widgets.types import Master


class FlexFrame(Frame):
    """A grid-backed 1-D flex container (the engine behind Row and Column).

    Lays children along a single main axis using the Tk *grid* geometry
    manager. Unlike pack, grid can express whole-group main-axis distribution
    (`justify`) without phantom spacer widgets — an empty track with a weight
    claims space on its own. That makes true weighted growth, correct
    `space-around`, and a `Spacer` element all expressible on one engine.

    Children are added through `add_child`, which appends to an ordered managed
    list and re-plans the whole layout (`_relayout`). Re-planning on every add
    is required because `justify`'s phantom tracks and the content-track indices
    shift as children come and go — the same approach `GridFrame` uses.

    Layout model (HStack == one row, N columns shown; Column transposes):

    - The single cross track always carries `weight=1` so `align`
      (start/center/end/stretch) has room to position a child even when the
      container is larger than its content.
    - `justify` injects phantom weighted tracks *between/around* the content
      cells (no widget) — only when nothing grows (grow defeats justify).
    - `grow` / `grow_items` / `weights=` put weight on the *content* tracks.
    - `Spacer` children occupy a real content track whose weight (flexible) or
      `minsize` (fixed) is taken from the spacer.
    - Gap is synthesized with edge-aware leading `padx`/`pady`, skipping the
      phantom and spacer breaks so it never doubles up around them.
    """

    def __init__(
        self,
        master: Master = None,
        *,
        direction: str = "horizontal",
        horizontal_items: str = "left",
        vertical_items: str = "top",
        grow_items: bool = False,
        weights: list[int] | None = None,
        gap: int = 0,
        propagate: bool | None = None,
        **kwargs: Unpack[FrameKwargs],
    ) -> None:
        """Create a FlexFrame.

        The public layout vocabulary is screen-axis based: `horizontal_items` and
        `vertical_items` set how children sit on the x and y axes (values are edge
        names — `left`/`right`/`top`/`bottom`/`center`/`stretch`, plus `space-*`
        for the stacking axis). Internally the frame resolves which screen axis is
        the *main* (stacking) axis and which is the *cross* axis from `direction`.

        Args:
            master: Parent widget. If None, uses the default root window.
            direction: Main axis — `'horizontal'` (a Row) or `'vertical'`
                (a Column). Defaults to `'horizontal'`.
            horizontal_items: How children are positioned on the x axis. For a
                Row (horizontal stacks) this arranges the group
                (`left`/`center`/`right`/`space-*`); for a Column it aligns each
                child (`left`/`center`/`right`/`stretch`). Defaults to `'left'`.
            vertical_items: How children are positioned on the y axis. For a
                Column (vertical stacks) this arranges the group
                (`top`/`center`/`bottom`/`space-*`); for a Row it aligns each
                child (`top`/`center`/`bottom`/`stretch`). Defaults to `'top'`.
            grow_items: When True, every content child grows equally (uniform)
                to share the main axis. Defaults to False.
            weights: Positional shorthand for per-child `grow` —
                `weights[i]` is the flex-grow weight of content child `i`
                (share of leftover main-axis space, not a fixed size). Overrides
                `grow_items` and per-child `grow`; missing trailing entries are
                0. Defaults to None.
            gap: Spacing in pixels between adjacent content children. Defaults
                to 0.
            propagate: When False, the frame does not resize to fit its
                children. Defaults to None (Tk default).

        Other Parameters:
            **kwargs: Additional keyword arguments forwarded to `Frame`.
        """
        super().__init__(master, **kwargs)
        self._direction = direction
        self._horizontal_items = horizontal_items
        self._vertical_items = vertical_items
        self._grow_items = grow_items
        self._weights = weights
        self._gap = gap
        # Ordered (widget, opts) entries. opts may carry: grow, horizontal,
        # vertical, padx, pady (resolved margins), and spacer metadata
        # (_spacer, _spacer_size, _spacer_weight).
        self._managed: list[tuple[tk.Widget, dict[str, Any]]] = []
        # Highest main-axis track index configured on the previous relayout,
        # so we can zero stale tracks when the plan shrinks.
        self._used_main_tracks = 0
        if propagate is not None:
            self.grid_propagate(propagate)

    # ----- direction helpers -------------------------------------------------

    @property
    def _row_dir(self) -> bool:
        """True when the main axis is horizontal (columns vary)."""
        return self._direction in ("horizontal", "row")

    def _main_distribution(self) -> str:
        """Normalize the stacking-axis value to start/center/end/space-* tokens."""
        if self._row_dir:
            value = self._horizontal_items
            start, end = "left", "right"
        else:
            value = self._vertical_items
            start, end = "top", "bottom"
        if value == start:
            return "start"
        if value == end:
            return "end"
        return value  # center, space-between, space-around, space-evenly

    def _cross_default(self) -> str:
        """The cross-axis (non-stacking) container alignment value."""
        return self._vertical_items if self._row_dir else self._horizontal_items

    def _cross_sticky(self, value: str) -> str:
        """Map a cross-axis edge value to Tk sticky chars for this direction."""
        if value == "stretch":
            return "ns" if self._row_dir else "ew"
        if self._row_dir:  # cross axis is vertical
            if value == "top":
                return "n"
            if value == "bottom":
                return "s"
        else:  # cross axis is horizontal
            if value == "left":
                return "w"
            if value == "right":
                return "e"
        return ""  # center

    def index_of(self, widget: tk.Widget) -> int:
        """Return the managed index of `widget`, or -1 if not managed."""
        for i, (w, _) in enumerate(self._managed):
            if w is widget:
                return i
        return -1

    # ----- child management --------------------------------------------------

    def add_child(
        self, widget: tk.Widget, opts: dict[str, Any], index: int | None = None
    ) -> None:
        """Add `widget` to the flow (at `index`, else appended) and re-plan."""
        entry = (widget, dict(opts))
        if index is None or index >= len(self._managed):
            self._managed.append(entry)
        else:
            self._managed.insert(max(index, 0), entry)
        self._relayout()

    def remove_child(self, widget: tk.Widget) -> None:
        """Remove `widget` from the flow (grid-forget it) and re-plan."""
        idx = self.index_of(widget)
        if idx < 0:
            return
        try:
            tk.Grid.forget(widget)
        except tk.TclError:
            pass
        self._managed.pop(idx)
        self._relayout()

    # ----- configuration delegates -------------------------------------------

    @configure_delegate('gap')
    def _delegate_gap(self, value=None) -> int:
        """Get or set the gap between children."""
        if value is None:
            return self._gap
        self._gap = value
        self._relayout()

    @configure_delegate('horizontal_items')
    def _delegate_horizontal_items(self, value=None) -> str:
        """Get or set how children are positioned on the x axis."""
        if value is None:
            return self._horizontal_items
        self._horizontal_items = value
        self._relayout()

    @configure_delegate('vertical_items')
    def _delegate_vertical_items(self, value=None) -> str:
        """Get or set how children are positioned on the y axis."""
        if value is None:
            return self._vertical_items
        self._vertical_items = value
        self._relayout()

    # ----- the planner -------------------------------------------------------

    def _grid_cell(
        self, widget: tk.Widget, idx: int, sticky: str, pad: dict[str, Any]
    ) -> None:
        """Place `widget` into main-track `idx` on the single cross track."""
        opts: dict[str, Any] = {"in_": self, "sticky": sticky, **pad}
        if self._row_dir:
            opts.update(row=0, column=idx)
        else:
            opts.update(column=0, row=idx)
        tk.Grid.configure(widget, **opts)

    def _relayout(self) -> None:
        """Re-plan and re-grid every managed child from scratch."""
        row_dir = self._row_dir
        main_cfg = self.grid_columnconfigure if row_dir else self.grid_rowconfigure
        cross_cfg = self.grid_rowconfigure if row_dir else self.grid_columnconfigure

        # Reposition surviving children IN PLACE — re-gridding an already-gridded
        # widget (grid_configure) moves it without an unmap/remap, so we must NOT
        # grid_forget them here: that would fire spurious <Unmap>/<Map> (and thus
        # on_detach/on_attach) on every sibling whenever one child is added or
        # removed. A genuinely removed child is grid-forgotten by remove_child
        # before this runs, so it is already out of self._managed.
        #
        # Zero the tracks the previous plan used so a now-shorter plan leaves no
        # stale weights/minsizes/uniform groups (configuring a track does not
        # touch the widgets in it).
        for i in range(self._used_main_tracks + 1):
            main_cfg(i, weight=0, minsize=0, uniform="")
        self._used_main_tracks = 0

        items = self._managed
        if not items:
            return

        # The cross track always fills so align has room to work.
        cross_cfg(0, weight=1)

        j = self._main_distribution()
        per_child_grow = any(
            o.get("grow") for _, o in items if not o.get("_spacer")
        )
        has_spacer = any(o.get("_spacer") for _, o in items)
        any_grow = (
            self._grow_items
            or per_child_grow
            or self._weights is not None
            or has_spacer
        )
        # justify only engages when nothing competes for the main axis.
        use_just = (not any_grow) and j != "start"
        uniform_grow = self._grow_items and not per_child_grow and self._weights is None

        # Build a plan of phantom breaks ('p', weight) and content ('c', w, o).
        plan: list[tuple] = []
        if use_just and j in ("end", "center", "space-evenly", "space-around"):
            plan.append(("p", 1))
        for i, (w, o) in enumerate(items):
            if i > 0 and use_just:
                if j in ("space-between", "space-evenly"):
                    plan.append(("p", 1))
                elif j == "space-around":
                    plan.append(("p", 2))
            plan.append(("c", w, o))
        if use_just and j in ("center", "space-evenly", "space-around"):
            plan.append(("p", 1))

        idx = 0
        content_seen = 0
        prev_content = False
        for entry in plan:
            if entry[0] == "p":
                main_cfg(idx, weight=entry[1])
                idx += 1
                prev_content = False
                continue

            _, widget, o = entry

            # Spacer: a real child whose track carries the slack/fixed size.
            if o.get("_spacer"):
                size = o.get("_spacer_size")
                if size is not None:
                    main_cfg(idx, weight=0, minsize=size)
                else:
                    main_cfg(idx, weight=o.get("_spacer_weight", 1))
                self._grid_cell(widget, idx, "", {})
                idx += 1
                prev_content = False
                continue

            # Content child: resolve its main-axis weight. `grow` is bool | int —
            # grow=True means weight 1, grow=N sets the relative weight. Coerce
            # bool to int so Tk's columnconfigure never sees a bool.
            weight = o.get("grow")
            if isinstance(weight, bool):
                weight = 1 if weight else 0
            if weight is None and self._grow_items:
                weight = 1
            if self._weights is not None:
                weight = (
                    int(self._weights[content_seen])
                    if content_seen < len(self._weights)
                    else 0
                )
            weight = int(weight or 0)
            grows = weight > 0
            if uniform_grow:
                main_cfg(idx, weight=weight, uniform="flex")
            else:
                main_cfg(idx, weight=weight)

            # Cross-axis sticky from the child's cross alignment (+ main-axis
            # stretch when growing). The cross axis is vertical for a Row and
            # horizontal for a Column, so the relevant per-child key flips.
            cross_key = "vertical" if row_dir else "horizontal"
            cross_val = o.get(cross_key) or self._cross_default()
            sticky = ""
            if grows:
                sticky += "ew" if row_dir else "ns"
            sticky += self._cross_sticky(cross_val)

            # Gap (leading, between content only) + per-child margins.
            main_axis = "padx" if row_dir else "pady"
            cross_axis = "pady" if row_dir else "padx"
            lead = self._gap if prev_content else 0
            trail = 0
            margin_main = o.get(main_axis)
            if isinstance(margin_main, tuple):
                lead += margin_main[0]
                trail = margin_main[1]
            elif margin_main is not None:
                lead += margin_main
            pad: dict[str, Any] = {}
            if lead or trail:
                pad[main_axis] = (lead, trail)
            margin_cross = o.get(cross_axis)
            if margin_cross is not None:
                pad[cross_axis] = margin_cross

            self._grid_cell(widget, idx, sticky, pad)
            idx += 1
            content_seen += 1
            prev_content = True

        self._used_main_tracks = max(idx - 1, 0)
