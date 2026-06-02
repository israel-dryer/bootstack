from __future__ import annotations

import tkinter
from typing import Any, Literal

from bootstack.widgets._impl.composites.scrollview import ScrollView as _InternalScrollView
from bootstack.widgets._core.container import PublicContainer, PACK_KEYS


class ScrollView(PublicContainer):
    """A canvas-based scrollable container.

    Place children inside the context block; they are laid out vertically
    inside the scrollable area. Mouse-wheel scrolling is automatically
    enabled for all descendants.

    Args:
        scroll_direction: Which axis to scroll — `'vertical'`, `'horizontal'`,
            or `'both'` (default).
        scrollbar_visibility: When scrollbars appear — `'always'` (default),
            `'never'`, `'hover'` (appears on mouse enter), or `'scroll'`
            (auto-hides after `autohide_delay` ms of inactivity).
        autohide_delay: Milliseconds before scrollbars hide in `'scroll'` mode.
            Default `1000`.
        scrollbar_variant: Style variant applied to both scrollbars.
            ``'default'`` for a rounded thumb (default), ``'square'`` for a
            flat rectangular thumb.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        *,
        scroll_direction: Literal["vertical", "horizontal", "both"] = "both",
        scrollbar_visibility: Literal["always", "never", "hover", "scroll"] = "always",
        autohide_delay: int = 1000,
        scrollbar_variant: str = "default",
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
            "scrollbar_variant": scrollbar_variant,
        }
        internal_kwargs.update(kwargs)

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