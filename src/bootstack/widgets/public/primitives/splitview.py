from __future__ import annotations

import tkinter
from typing import Any

from bootstack.widgets.primitives.panedwindow import PanedWindow as _InternalPanedWindow
from bootstack.widgets.primitives.frame import Frame as _InternalFrame
from bootstack.widgets.public.base import PublicWidgetBase
from bootstack.widgets.public.container import PACK_KEYS, normalize_fill
from bootstack.widgets.public.context import push_container, pop_container


class _SplitPane:
    """Context-manager for placing children inside a SplitView pane."""

    def __init__(self, frame: tkinter.Widget) -> None:
        self._frame = frame

    def _child_master(self) -> tkinter.Widget:
        return self._frame

    def guide_layout(self, child: PublicWidgetBase, **layout_kw: Any) -> None:
        options = {k: v for k, v in layout_kw.items() if k in PACK_KEYS}
        child._internal.pack(in_=self._frame, **options)

    def __enter__(self) -> "_SplitPane":
        push_container(self)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pop_container(self)


class SplitView(PublicWidgetBase):
    """A resizable split container with one or more panes separated by draggable sashes.

    Add panes with `.add()` and place children inside each pane using the
    returned context manager.

    Usage::

        sv = bs.SplitView(fill="both", expand=True)
        with sv.add(weight=1):
            bs.Label("Left pane")
        with sv.add(weight=2):
            bs.Label("Right pane")

    Args:
        orient: `'horizontal'` (default, panes side-by-side) or `'vertical'` (stacked).
        padding: Space around the pane area.
        accent: Accent token for styling.
        width: Requested width in pixels.
        height: Requested height in pixels.
        fill: Self-placement fill direction in parent.
        expand: Self-placement expand flag.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        orient: str = "horizontal",
        *,
        padding: Any = None,
        accent: str | None = None,
        width: int | None = None,
        height: int | None = None,
        # Self-placement
        fill: str | None = None,
        expand: bool | None = None,
        anchor: str | None = None,
        parent: Any = None,
        **extra_kw: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)

        layout_kw: dict[str, Any] = {}
        if fill is not None:
            layout_kw["fill"] = normalize_fill(fill)
        if expand is not None:
            layout_kw["expand"] = expand
        if anchor is not None:
            layout_kw["anchor"] = anchor
        layout_kw.update(self._split_layout_kwargs(extra_kw))

        pw_kwargs: dict[str, Any] = {"orient": orient}
        if padding is not None:
            pw_kwargs["padding"] = padding
        if accent is not None:
            pw_kwargs["accent"] = accent
        if width is not None:
            pw_kwargs["width"] = width
        if height is not None:
            pw_kwargs["height"] = height
        pw_kwargs.update(extra_kw)

        tk_master = self._parent._child_master() if self._parent else None
        self._internal = _InternalPanedWindow(tk_master, **pw_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Pane management -----

    def add(self, *, weight: int = 1) -> _SplitPane:
        """Add a pane and return a context manager for placing its children.

        Usage::

            with sv.add(weight=1):
                bs.Label("Content")

        Args:
            weight: Relative size weight when the container is resized.
                Higher values take proportionally more space.

        Returns:
            `_SplitPane` — use as a context manager to place children.
        """
        frame = _InternalFrame(self._internal)
        self._internal.add(frame, weight=weight)
        return _SplitPane(frame)

    # ----- Sash control -----

    def sash_position(self, index: int, position: int | None = None) -> int | None:
        """Get or set the position of a sash.

        Args:
            index: Zero-based sash index.
            position: New position in pixels. If `None`, returns the current position.

        Returns:
            Current sash position in pixels when `position` is `None`.
        """
        if position is None:
            return self._internal.sashpos(index)
        self._internal.sashpos(index, position)
        return None