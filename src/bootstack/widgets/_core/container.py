from __future__ import annotations

import tkinter
from typing import Any, Literal

PACK_KEYS = frozenset({
    "side", "fill", "expand", "anchor",
    "padx", "pady", "ipadx", "ipady",
    "margin", "margin_x", "margin_y",
    "index", "before", "after", "in_",
})

GRID_KEYS = frozenset({
    "row", "column", "rowspan", "columnspan",
    "sticky", "padx", "pady", "ipadx", "ipady",
    "margin", "margin_x", "margin_y",
    "in_",
})

PLACE_KEYS = frozenset({
    "x", "y", "relx", "rely",
    "width", "height", "relwidth", "relheight",
    "anchor", "bordermode", "in_",
})

# Per-child placement keys for the flex/grid layout engine (Row/Column/Grid).
# Collision-free by design — never bare `align`/`justify`, which would shadow
# Label/TextField text `justify` and Snackbar `align` on every widget.
FLEX_CHILD_KEYS = frozenset({
    "grow", "horizontal", "vertical",
    "margin", "margin_x", "margin_y", "index",
})

# Legacy pack/grid placement kwargs the flex engine deliberately rejects, so a
# stale `fill=`/`expand=`/`anchor=`/`sticky=` raises a clear migration error
# instead of silently collapsing a child (data/canvas widgets especially).
_LEGACY_CHILD_KEYS = frozenset({"fill", "expand", "anchor", "sticky", "side"})

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
    """Convert margin=/marginx=/marginy= to padx=/pady= in-place.

    Processing order: margin sets both axes as a baseline; marginx and
    marginy override their respective axis. Explicit padx/pady always win.
    """
    margin = layout_kw.pop("margin", None)
    marginx = layout_kw.pop("margin_x", None)
    marginy = layout_kw.pop("margin_y", None)

    padx = pady = None

    if margin is not None:
        if isinstance(margin, (int, float)):
            padx = pady = margin
        elif len(margin) == 2:
            padx, pady = margin  # (horizontal, vertical)
        else:
            left, top, right, bottom = margin
            padx = (left, right)
            pady = (top, bottom)

    if marginx is not None:
        padx = marginx
    if marginy is not None:
        pady = marginy

    if padx is not None:
        layout_kw.setdefault("padx", padx)
    if pady is not None:
        layout_kw.setdefault("pady", pady)


# ---  PublicContainer  -------------------------------------------------------
# Imported here (after constants) to avoid circular imports in base.py.

from bootstack.widgets._core.base import PublicWidgetBase  # noqa: E402
from bootstack.widgets._core.context import push_container, pop_container  # noqa: E402


class Placement:
    """Snapshot of how a widget was placed, enabling `detach`/`attach`.

    Recorded on the child at layout time by `guide_layout`; consumed by
    `PublicWidgetBase.detach`/`attach` to remove and re-insert the widget
    without re-running its constructor. `options` holds the resolved Tk
    geometry-manager options (no ordering refs); `index` is the pack position
    among siblings, snapshotted afresh on each `detach`.
    """

    __slots__ = ("method", "master", "options", "index")

    def __init__(
        self,
        method: str,
        master: tkinter.Misc,
        options: dict,
        index: int | None = None,
    ) -> None:
        self.method = method      # "pack" | "grid" | "place"
        self.master = master      # the Tk master the child is placed in
        self.options = options    # resolved Tk options (no before/after/index)
        self.index = index        # pack order among siblings (snapshot at detach)


def resolve_pack_order(order: dict, master: tkinter.Misc) -> dict:
    """Translate public `index`/`before`/`after` into a Tk pack-order kwarg.

    Pops the ordering keys from `order` and returns the corresponding Tk
    `pack()` kwarg dict. `index=` is the position among the master's currently
    packed children, translated to `before=<that child>` (appended when the
    index is past the end). Explicit `before=`/`after=` accept either a public
    widget or a raw Tk widget. `before` wins over `after` wins over `index`.
    """
    index = order.pop("index", None)
    before = order.pop("before", None)
    after = order.pop("after", None)
    if before is not None:
        return {"before": getattr(before, "_internal", before)}
    if after is not None:
        return {"after": getattr(after, "_internal", after)}
    if index is not None:
        slaves = master.pack_slaves()
        if 0 <= index < len(slaves):
            return {"before": slaves[index]}
    return {}


class PublicContainer(PublicWidgetBase):
    """Base for public containers (Row, Column, Grid, App).

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
        """Place `child._internal` under this container.

        Records a `Placement` snapshot on the child so it can later be
        `detach`-ed and `attach`-ed. When `attached=False` is passed, the
        snapshot is recorded but the widget is NOT mapped — it starts hidden,
        ready to be shown with `attach`.
        """
        attached = layout_kw.pop("attached", True)
        if "fill" in layout_kw:
            layout_kw["fill"] = normalize_fill(layout_kw["fill"])
        _expand_margin(layout_kw)
        place_mode = any(k in layout_kw for k in PLACE_TRIGGER_KEYS)
        tk_widget = child._internal
        master = self._child_master()

        if place_mode:
            options = {k: v for k, v in layout_kw.items() if k in PLACE_KEYS}
            if attached:
                tk_widget.place(in_=master, **options)
            child._placement = Placement("place", master, options)
            return

        method, options = self._merge_layout_options(child, layout_kw)
        if method == "pack":
            # Capture an explicit index before resolve_pack_order strips it.
            explicit_index = options.get("index")
            order_kw = resolve_pack_order(options, master)  # mutates options
            if attached:
                tk_widget.pack(in_=master, **options, **order_kw)
                child._placement = Placement("pack", master, dict(options))
            else:
                # Remember the slot a later attach() should restore: an
                # explicit index if given, else the natural append position
                # (the count of siblings already packed at this point).
                index = explicit_index if explicit_index is not None else len(master.pack_slaves())
                child._placement = Placement("pack", master, dict(options), index=index)
        elif method == "grid":
            if attached:
                tk_widget.grid(in_=master, **options)
            child._placement = Placement("grid", master, dict(options))
        else:
            raise ValueError(f"Unknown layout method: {method!r}")

    def __enter__(self) -> "PublicContainer":
        push_container(self)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pop_container(self)
        return None


# ---  Flex engine (Row / Column)  --------------------------------------------


# Per-child keys a GRID CELL honors. `grow=` is deliberately ABSENT: Grid and
# the page/pane containers filter their child options to GRID_KEYS, so a `grow=`
# written on one of their children is silently dropped. `sticky`/`in_` are not
# user-facing — `sticky` is a legacy key the guard below rejects, and the cell
# derives it from `horizontal`/`vertical` instead.
GRID_CHILD_KEYS = (GRID_KEYS | {"horizontal", "vertical"}) - {"sticky", "in_"}

_ALIGN_ADVICE = (
    "horizontal= takes left/center/right/stretch and vertical= takes "
    "top/center/bottom/stretch (for example horizontal=\"stretch\")"
)

# The remedy depends on HOW the container places its children, and naming the
# wrong one is the defect this message exists to fix (issue #426). A flex
# container honors `grow=` on the child; a grid cell drops it, so recommending
# it there would send the user to a kwarg that does nothing — the same silent
# no-op #426 was filed about, just one step further along.
FLEX_CHILD_ADVICE = (
    "Use grow= to claim leftover space along the stacking axis, or "
    "horizontal=/vertical= to align or stretch across it — " + _ALIGN_ADVICE
)

# Container-level options are named WITHOUT a trailing `=` on purpose: the `X=`
# spelling is reserved for per-child remedies, which is what the regression test
# checks must be real keys.
GRID_CHILD_ADVICE = (
    "Use horizontal=/vertical= to align or stretch the child inside its cell — "
    + _ALIGN_ADVICE
    + ". Leftover space is claimed by weighting the row or column on the "
    "container (its columns/rows arguments), not by a kwarg on the child"
)

# The kind names the child's PLACEMENT, not its parent class: the dual-mode
# containers (Card/GroupBox/Expander/AccordionSection) are one or the other
# depending on their `layout=`, and the page/pane containers are grid cells
# without a `Grid` anywhere in sight.
ChildKind = Literal["flex child", "grid cell"]

_CHILD_ADVICE: dict[str, str] = {
    "flex child": FLEX_CHILD_ADVICE,
    "grid cell": GRID_CHILD_ADVICE,
}


def _reject_legacy_child_kwargs(layout_kw: dict, where: str, kind: ChildKind) -> None:
    """Raise on legacy pack/grid placement kwargs passed to a laid-out child.

    Args:
        layout_kw: the split-out layout kwargs to inspect.
        where: the call site named in the message.
        kind: how this container places the child — `'flex child'` or
            `'grid cell'`. It selects the remedy, and the two differ: a grid
            cell drops `grow=`, so recommending it there is the silent no-op
            issue #426 exists to remove. Required rather than defaulted,
            because a default hands the wrong advice to any caller who forgets
            — which is how four call sites kept the defect through its own fix.
    """
    bad = _LEGACY_CHILD_KEYS & layout_kw.keys()
    if bad:
        from bootstack.errors import BootstackError

        # KeyError on an unknown kind is deliberate: a mistyped kind must fail
        # loudly here rather than quietly pick a remedy for the other engine.
        advice = _CHILD_ADVICE[kind]
        raise BootstackError(
            f"{where}: {', '.join(sorted(bad))} is not a valid layout option for "
            f"a {kind}. {advice} — see the layout guide."
        )


def grid_sticky(horizontal: str | None, vertical: str | None) -> str:
    """Derive a Tk `sticky` string from in-cell alignment edge values.

    `horizontal` is `left`/`center`/`right`/`stretch`, `vertical` is
    `top`/`center`/`bottom`/`stretch`. `stretch` fills the axis, the edge values
    pin to that edge, and `center` (or None) leaves the axis unpinned so the
    child sits centered in the cell.
    """
    sticky = ""
    if horizontal == "stretch":
        sticky += "ew"
    elif horizontal == "left":
        sticky += "w"
    elif horizontal == "right":
        sticky += "e"
    if vertical == "stretch":
        sticky += "ns"
    elif vertical == "top":
        sticky += "n"
    elif vertical == "bottom":
        sticky += "s"
    return sticky


def resolve_layout_items(
    layout: str,
    horizontal_items: str | None,
    vertical_items: str | None,
    *,
    column_horizontal: str | None = None,
) -> tuple[str | None, str | None]:
    """Fill in a multi-mode container's unset `*_items` for its layout mode.

    Containers that can lay out as a column, a row, or a grid (`Card`, `GroupBox`,
    `Expander`, `Tabs`, `PageStack`, `SplitView`, the AppShell page) take
    `horizontal_items`/`vertical_items` as `None`-means-unset and need a default
    that depends on the mode.

    A **grid** gets concrete values, because the grid engine has no notion of an
    unset axis — cells stretch unless told otherwise. A **column** or **row**
    keeps `None` and lets `FlexFrame` resolve it: the engine's own defaults are
    exactly what these containers used to hard-code (the stacking axis starts at
    its leading edge, the cross axis centers), and leaving the cross axis unset is
    what allows a child to contribute its own default — which is how a row of
    input fields stays aligned whether or not each field carries a validation
    message (#394). Pre-resolving to `'center'` here silently suppressed that.

    Args:
        layout: The container's layout mode — `'column'`, `'row'` or `'grid'`.
        horizontal_items: The x-axis value as given, or None if unset.
        vertical_items: The y-axis value as given, or None if unset.
        column_horizontal: Cross-axis override for column mode, for a container
            whose column should not center — the AppShell page stretches instead.
            Defaults to None (use the engine default).

    Returns:
        The pair to hand the layout frame. Either element may be None in column or
        row mode, meaning "unset — let the engine decide"; both are concrete for a
        grid. The None is only ever passed to `FlexFrame`; the grid path
        (`_merge_layout_options`) runs solely in grid mode, where both are set.
    """
    if layout == "grid":
        return (horizontal_items or "stretch", vertical_items or "stretch")
    if layout == "column" and horizontal_items is None:
        horizontal_items = column_horizontal
    return (horizontal_items, vertical_items)


def _flex_child_opts(child: PublicWidgetBase, layout_kw: dict) -> dict:
    """Build the FlexFrame per-child opts dict from resolved layout kwargs.

    Expects `_expand_margin` to have already converted margins to padx/pady.
    Carries spacer metadata when `child` is a `Spacer` (duck-typed to avoid a
    circular import).

    A widget may also declare its own preferred cross-axis alignment via a
    `_flex_horizontal_default` / `_flex_vertical_default` class attribute (same
    duck-typing). That is a *soft* default: it applies only when neither the
    child nor the container was given an explicit alignment, so it can never
    override an instruction the author actually wrote. The field family uses it
    to sit top-aligned in a Row instead of centering, since a field carrying a
    validation message is taller than one that isn't (#394).
    """
    opts: dict[str, Any] = {}
    for key in ("grow", "horizontal", "vertical", "padx", "pady"):
        if key in layout_kw:
            opts[key] = layout_kw[key]
    for axis in ("horizontal", "vertical"):
        if axis not in opts:
            declared = getattr(child, f"_flex_{axis}_default", None)
            if declared is not None:
                opts[f"_{axis}_default"] = declared
    if getattr(child, "_is_spacer", False):
        opts["_spacer"] = True
        opts["_spacer_size"] = getattr(child, "_spacer_size", None)
        opts["_spacer_weight"] = getattr(child, "_spacer_weight", 1)
    return opts


class FlexContainer(PublicContainer):
    """Base for containers whose children flow through a `FlexFrame`.

    Subclasses build a `FlexFrame` and expose it via `_flex_frame`; children
    are added to it (re-planning the layout) and a `Placement(method="flex")`
    is recorded for `detach`/`attach`. Defaults `_flex_frame` to `_internal`,
    which suits the stack widgets; containers with a nested layout frame (App's
    content frame, Card's body) override the property.
    """

    @property
    def _flex_frame(self) -> Any:
        return self._internal

    def _child_master(self) -> tkinter.Misc:
        return self._flex_frame

    def _default_layout_method(self) -> str:
        return "flex"

    def guide_layout(self, child: PublicWidgetBase, **layout_kw: Any) -> None:
        """Place `child` into this container's flow and snapshot its placement."""
        place_flex_child(self._flex_frame, child, layout_kw, type(self).__name__)


def place_flex_child(
    frame: Any, child: PublicWidgetBase, layout_kw: dict, where: str
) -> None:
    """Add `child` to a `FlexFrame` and record a `Placement` for detach/attach.

    Shared by `FlexContainer` and the dual-mode containers (Card/GroupBox in
    their column/row mode) so the flex placement contract lives in one place.
    Absolute placement (`x=`/`y=`) is honored as an overlay escape hatch — the
    child is `place`-d over the flow rather than entering it.
    """
    attached = layout_kw.pop("attached", True)

    # Place-mode escape hatch: a child given x/y/relx/rely is positioned
    # absolutely over the flow, not gridded into it.
    if any(k in layout_kw for k in PLACE_TRIGGER_KEYS):
        options = {k: v for k, v in layout_kw.items() if k in PLACE_KEYS}
        if attached:
            child._internal.place(in_=frame, **options)
        child._placement = Placement("place", frame, options)
        return

    _reject_legacy_child_kwargs(layout_kw, where, "flex child")
    _expand_margin(layout_kw)
    index = layout_kw.get("index")
    opts = _flex_child_opts(child, layout_kw)
    if attached:
        frame.add_child(child._internal, opts, index=index)
        child._placement = Placement("flex", frame, opts)
    else:
        # Record the slot a later attach() restores: an explicit index, else the
        # natural append position (current child count).
        if index is None:
            index = len(frame._managed)
        child._placement = Placement("flex", frame, opts, index=index)
