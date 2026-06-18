from __future__ import annotations

from tkinter import ttk
from typing import Any

from typing_extensions import Unpack

from bootstack._core.mixins.ttk_state import TtkStateMixin
from bootstack._core.mixins.widget import WidgetCapabilitiesMixin
from bootstack.widgets._impl._internal.wrapper_base import TTKWrapperBase
from bootstack.widgets.types import Master, StyledKwargs
from bootstack.style.style import get_style
from ..mixins import configure_delegate


class FrameKwargs(StyledKwargs, total=False):
    # Standard ttk.Frame options
    padding: Any
    width: int
    height: int

    # bootstack-specific extensions
    input_background: str
    show_border: bool


class Frame(TTKWrapperBase, WidgetCapabilitiesMixin, TtkStateMixin, ttk.Frame):
    """bootstack wrapper for `ttk.Frame` with themed styling support."""

    _ttk_base = ttk.Frame

    def __init__(self, master: Master = None, **kwargs: Unpack[FrameKwargs]) -> None:
        """Create a themed bootstack Frame.

        Args:
            master: Parent widget. If None, uses the default root window.

        Other Parameters:
            padding: Extra padding inside the frame.
            relief: Border style.
            borderwidth: Border width.
            width: Requested width in pixels.
            height: Requested height in pixels.
            takefocus: Widget accepts focus during keyboard traversal.
            style: Explicit ttk style name (overrides accent/variant).
            accent: Accent token for styling, e.g. 'primary', 'secondary', 'success'.
            variant: Style variant (if applicable).
            surface: Optional surface token; otherwise inherited.
            input_background: Surface token used as the fill color for all input
                widgets (Entry, Combobox, Spinbox, Field) inside this container. Cascades
                to descendants the same way `surface` does. Input foreground, border,
                and focus-ring colors are all derived from this fill so contrast is always
                correct. Defaults to `'content'` (the app background), which keeps
                inputs visually distinct regardless of the container surface. Override
                with any surface token (e.g. `'card'`) to match the container.
            show_border: Draw a border around the frame.
            style_options: Optional dict forwarded to the style builder.
        """
        existing = kwargs.pop('style_options', {})
        captured = self._capture_style_options(['show_border'], kwargs)
        kwargs['style_options'] = {**existing, **captured}
        super().__init__(master, **kwargs)

    # ----- Theme repaint (for imperatively-painted / canvas widgets) -----

    def _enable_theme_repaint(self, repaint) -> None:
        """Repaint canvas-painted content on theme change, gated on visibility.

        Widgets that paint colors directly onto a canvas live outside the ttk
        style loop, so they must re-resolve and redraw when the theme changes.
        Calling this once (after the drawing surface exists) wires that up the
        right way:

        - It subscribes to the `STD` publisher channel, which fires AFTER the
          theme rebuild (so resolved colors are the new theme's) and calls back
          directly (virtual events do not reach descendants).
        - The redraw runs ONLY while the widget is on screen. A theme change that
          arrives while it is off-screen (e.g. an inactive page) is deferred to
          the next `<Map>` — so a theme toggle repaints just the visible widgets
          instead of every canvas widget in the app.
        - The subscription is released on `<Destroy>`.

        Args:
            repaint: The widget's full re-resolve-and-redraw callback (no args).
        """
        from bootstack._core.publisher import Channel, Publisher

        self._theme_repaint = repaint
        self._theme_repaint_pending = False
        name = str(self)
        Publisher.subscribe(name=name, func=self._on_theme_notify, channel=Channel.STD)
        self.bind('<Map>', self._on_theme_map, add='+')
        self.bind('<Destroy>', lambda _e, n=name: Publisher.unsubscribe(n), add='+')

    def _on_theme_notify(self, *_: Any, **__: Any) -> None:
        """STD-publisher callback (after the rebuild): repaint now, or defer."""
        if not self.winfo_exists():
            return
        if self.winfo_viewable():
            self._theme_repaint_pending = False
            self._theme_repaint()
        else:
            self._theme_repaint_pending = True

    def _on_theme_map(self, _event: Any = None) -> None:
        """On map, run a theme repaint that was deferred while off-screen."""
        if getattr(self, '_theme_repaint_pending', False):
            # Defer to idle so the repaint runs after the map cascade settles
            # (a canvas background can be reset to the default during mapping).
            self.after_idle(self._run_pending_theme_repaint)

    def _run_pending_theme_repaint(self) -> None:
        if getattr(self, '_theme_repaint_pending', False) and self.winfo_exists():
            self._theme_repaint_pending = False
            self._theme_repaint()

    def configure_style_options(self, value=None, **kwargs):
        """Set style options and refresh descendant surfaces if needed."""
        old_surface = getattr(self, "_surface", "background")
        old_input_bg = getattr(self, "_input_background", None)
        result = super().configure_style_options(value, **kwargs)
        if value is None:
            if "surface" in kwargs:
                new_surface = getattr(self, "_surface", "background")
                if old_surface != new_surface:
                    self.rebuild_style()
                    self._refresh_descendant_surfaces(old_surface, new_surface)
            if "input_background" in kwargs:
                new_input_bg = getattr(self, "_input_background", None)
                if old_input_bg != new_input_bg:
                    self._refresh_descendant_input_backgrounds(old_input_bg, new_input_bg)
        return result

    def _refresh_descendant_surfaces(self, old_surface: str, new_surface: str) -> None:
        if old_surface == new_surface:
            return

        style = get_style()
        builder_tk = style._get_tk_builder()

        for child in self._iter_descendants():
            try:
                child_surface = getattr(child, "_surface", None)
            except Exception:
                child_surface = None

            explicit_surface = None
            try:
                explicit_surface = getattr(child, "_style_options", {}).get("surface")
            except Exception:
                explicit_surface = None

            if explicit_surface and explicit_surface != old_surface:
                continue

            if child_surface != old_surface:
                continue

            try:
                setattr(child, "_surface", new_surface)
            except Exception:
                continue

            if hasattr(child, "rebuild_style"):
                try:
                    child.rebuild_style()
                except Exception:
                    pass
            else:
                try:
                    builder_tk.call_builder(child, surface=new_surface)
                except Exception:
                    pass

    def _refresh_descendant_input_backgrounds(self, old_bg: str | None, new_bg: str | None) -> None:
        if old_bg == new_bg:
            return

        style = get_style()
        builder_tk = style._get_tk_builder()

        for child in self._iter_descendants():
            try:
                child_input_bg = getattr(child, "_input_background", None)
            except Exception:
                child_input_bg = None

            explicit_input_bg = None
            try:
                explicit_input_bg = getattr(child, "_style_options", {}).get("input_background")
            except Exception:
                explicit_input_bg = None

            if explicit_input_bg and explicit_input_bg != old_bg:
                continue

            if child_input_bg != old_bg:
                continue

            try:
                setattr(child, "_input_background", new_bg)
            except Exception:
                continue

            if hasattr(child, "rebuild_style"):
                try:
                    child.rebuild_style()
                except Exception:
                    pass
            else:
                try:
                    builder_tk.call_builder(child, input_background=new_bg)
                except Exception:
                    pass

    def _iter_descendants(self):
        stack = list(self.winfo_children())
        while stack:
            widget = stack.pop()
            yield widget
            try:
                stack.extend(widget.winfo_children())
            except Exception:
                pass

    @configure_delegate('show_border')
    def _delegate_show_border(self, value=None):
        """Get or set whether to draw a border."""
        if value is not None:
            return self.configure_style_options('show_border')
        else:
            self.configure_style_options(show_border=True)
            return self.rebuild_style()
