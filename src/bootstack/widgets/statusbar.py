from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from bootstack.widgets._impl.composites.toolbar import Toolbar as _InternalToolbar
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets.types import SurfaceToken, WidgetDensity

if TYPE_CHECKING:
    from bootstack.signals import Signal


class StatusBar(PublicWidgetBase):
    """A horizontal status band of passive segments — counts, sync state, a ready
    message.

    Intended for *passive* status (whether static or bound to a `Signal` for live
    updates). Interactive controls (buttons, a search box) belong on a
    :class:`CommandBar <bootstack.CommandBar>` by convention; nothing enforces it,
    but the status bar reads best as a quiet display strip. Segments add
    left-to-right; an `add_spacer()` (or `side='right'`) pushes the following
    segments to the right cluster.

    Use it standalone — ``bs.StatusBar(fill="x", side="bottom")`` pins one to the
    bottom of any `App`/`Window` — or read `shell.statusbar` for the one built
    into an :class:`AppShell <bootstack.AppShell>`. Create custom widgets with
    ``parent=statusbar`` (they add to the left cluster automatically) or pass a
    pre-parented widget to `add_widget()`.

    Args:
        surface: Background surface token. Defaults to the theme's `'chrome'`
            surface (a quiet band, distinct from the content area).
        density: Size of the band's segments. Default `'compact'`.
        padding: Inner padding in pixels — an int or a `(horizontal, vertical)`
            tuple. Defaults to a thin compact padding.
        parent: Override the context-stack parent.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `side`, `expand`, `anchor`, `margin`. See :doc:`/tasks/layout`.
    """

    _auto_place = True

    def __init__(
        self,
        *,
        surface: SurfaceToken | str | None = "chrome",
        density: WidgetDensity = "compact",
        padding: int | tuple[int, int] | None = None,
        parent: Any = None,
        _toolbar: Any = None,
        _show: Any = None,
        **kwargs: Any,
    ) -> None:
        self._has_right_spacer = False
        if _toolbar is not None:
            # Shell adoption: wrap the AppShell's pre-built status band. `_show`
            # reveals the (content-driven) band on the first segment added.
            self._internal = _toolbar
            self._parent = None
            self._show = _show or (lambda: None)
            return

        # Standalone: build our own bar (the CommandBar pattern).
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None
        internal_kwargs: dict[str, Any] = {"density": density, "draggable": False}
        if surface is not None:
            internal_kwargs["surface"] = surface
        if padding is not None:
            internal_kwargs["padding"] = padding
        internal_kwargs.update(kwargs)
        self._internal = _InternalToolbar(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)
        # Standalone bars are placed/shown by the caller — nothing to reveal.
        self._show = lambda: None

    # ----- Container protocol (so `parent=statusbar` works) -----

    def _child_master(self) -> Any:
        return self._internal.content

    def guide_layout(self, child: Any, **layout_kw: Any) -> None:
        # A widget created with `parent=statusbar` adds to the left cluster.
        self._internal.add_widget(child._internal)
        self._show()

    @property
    def content(self) -> Any:
        """The band's content frame — parent custom widgets here."""
        return self._internal.content

    # ----- Segments -----

    def _ensure_right(self) -> None:
        if not self._has_right_spacer:
            self._internal.add_spacer()
            self._has_right_spacer = True

    def add_widget(self, widget: Any, *, side: Literal["left", "right"] = "left") -> None:
        """Add a passive widget to the left or right cluster.

        Args:
            widget: A public widget (or raw internal widget) parented to this
                status bar's `content` frame.
            side: `'left'` (default) or `'right'` (after the spacer).
        """
        if side == "right":
            self._ensure_right()
        tk_widget = getattr(widget, "_internal", widget)
        self._internal.add_widget(tk_widget)
        self._show()

    def add_text(
        self,
        text: str = "",
        *,
        textsignal: "Signal | None" = None,
        side: Literal["left", "right"] = "left",
        icon: str | None = None,
        font: str | None = None,
    ) -> None:
        """Add a text (and optional icon) segment to a cluster.

        Pass `textsignal` to make the segment **reactive** — a `Signal` whose
        value drives the text and updates it live as the signal changes (e.g. a
        running count or sync state). `text` seeds a static segment instead.

        Args:
            text: The static label text (ignored when `textsignal` is given).
            textsignal: A reactive `Signal[str]` bound to the segment's text.
            side: `'left'` (default) or `'right'` (after the spacer).
            icon: Optional icon name displayed beside the text.
            font: Optional font token, e.g. `'caption'`.
        """
        if side == "right":
            self._ensure_right()
        kwargs: dict[str, Any] = {"icon": icon, "font": font}
        if textsignal is not None:
            kwargs["textsignal"] = textsignal
        self._internal.add_label(text, **kwargs)
        self._show()

    def add_spacer(self) -> None:
        """Add a flexible spacer that pushes following items to the right."""
        self._internal.add_spacer()
        self._has_right_spacer = True
        self._show()

    def clear(self) -> None:
        """Remove all status segments."""
        for child in list(self._internal.content.winfo_children()):
            try:
                child.destroy()
            except Exception:
                pass
        self._has_right_spacer = False
