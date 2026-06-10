from __future__ import annotations

import tkinter
from typing import Any, Literal

from bootstack.widgets._impl.composites.scrollview import ScrollView as _InternalScrollView
from bootstack.widgets._core.container import PublicContainer, PACK_KEYS
from bootstack.widgets.types import Padding


class ScrollView(PublicContainer):
    """A canvas-based scrollable container.

    Place children inside the context block; they are laid out vertically
    inside the scrollable area. Mouse-wheel scrolling is automatically
    enabled for all descendants.

    Args:
        scroll_direction: Which axis to scroll. Defaults to `'both'`.
        scrollbar_visibility: When scrollbars appear — `'always'` (default),
            `'never'`, `'hover'` (appears on mouse enter), or `'scroll'`
            (auto-hides after `autohide_delay` ms of inactivity).
        autohide_delay: Milliseconds before scrollbars hide in `'scroll'` mode.
            Defaults to `1000`.
        height: Fixed height of the viewport in pixels. When set, the
            canvas is pinned to this height regardless of content size.
            Required for vertical scrolling unless the parent already
            constrains the height. Defaults to `None`.
        width: Fixed width of the viewport in pixels. Pins the canvas
            width, similar to `height=`. Defaults to `None`.
        show_border: Draw a 1 px border around the ScrollView frame.
            Defaults to `False`.
        padding: Space in pixels between the border and the canvas.
            Defaults to `None` (no padding).
        parent: Override the context-stack parent.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        *,
        scroll_direction: Literal["vertical", "horizontal", "both"] = "both",
        scrollbar_visibility: Literal["always", "never", "hover", "scroll"] = "always",
        autohide_delay: int = 1000,
        height: int | None = None,
        width: int | None = None,
        show_border: bool = False,
        padding: Padding | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "scroll_direction": scroll_direction,
            "scrollbar_visibility": scrollbar_visibility,
            "autohide_delay": autohide_delay,
        }
        if height is not None:
            internal_kwargs["height"] = height
        if width is not None:
            internal_kwargs["width"] = width
        if show_border:
            internal_kwargs["show_border"] = True
        if padding is not None:
            internal_kwargs["padding"] = padding

        self._internal = _InternalScrollView(tk_master, **internal_kwargs)
        self._content_frame = self._internal.add()
        self._attach_to_parent(layout_kw)

    def _child_master(self) -> tkinter.Misc:
        return self._content_frame

    def _default_layout_method(self) -> str:
        return "pack"

    def _merge_layout_options(self, child: Any, layout_kw: dict) -> tuple[str, dict]:
        options = {k: v for k, v in layout_kw.items() if k in PACK_KEYS}
        return ("pack", options)

    # ----- Scrolling -----

    def enable_scrolling(self) -> None:
        """Enable mouse-wheel scrolling on the canvas and all children."""
        self._internal.enable_scrolling()

    def disable_scrolling(self) -> None:
        """Disable mouse-wheel scrolling on the canvas and all children."""
        self._internal.disable_scrolling()

    def refresh_bindings(self) -> None:
        """Refresh scroll bindings after dynamically adding many children."""
        self._internal.refresh_bindings()

    def scroll_to_top(self) -> None:
        """Scroll to the top of the content."""
        self._internal.yview_moveto(0.0)

    def scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the content."""
        self._internal.yview_moveto(1.0)

    def scroll_to_left(self) -> None:
        """Scroll to the left edge of the content."""
        self._internal.xview_moveto(0.0)

    def scroll_to_right(self) -> None:
        """Scroll to the right edge of the content."""
        self._internal.xview_moveto(1.0)

    def yview_moveto(self, fraction: float) -> None:
        """Scroll to a vertical position.

        Args:
            fraction: 0.0 (top) to 1.0 (bottom).
        """
        self._internal.yview_moveto(fraction)

    def xview_moveto(self, fraction: float) -> None:
        """Scroll to a horizontal position.

        Args:
            fraction: 0.0 (left) to 1.0 (right).
        """
        self._internal.xview_moveto(fraction)