"""Layer 1 — the region/slot band layout for the application shell.

`ShellLayout` owns the window (it subclasses the internal `App`) and arranges
the shell's bands as independently toggleable slots:

    +-------------------------------------------------+
    | chrome   (top, full width)                      |
    +----+--------------+------------------+----------+
    | r  | sidebar      |     content      |   dock   |
    | a  |              |                  | (resv'd) |
    | i  |              |                  |          |
    | l  |              |                  |          |
    +----+--------------+------------------+----------+
    | statusbar   (full width)                        |
    +-------------------------------------------------+

This layer is deliberately **dumb about navigation** — it exposes region frames
and show/hide/size operations only. Wiring the regions to `NavModel` (which
workspace/page is active, the rail gesture, etc.) happens in a higher layer.

The top (`chrome`) and bottom (`statusbar`) bands span the full window width;
only the body row knows whether the rail/sidebar/dock exist. That invariant lets
"sidebar + chrome", "chrome only", and "sidebar only" be the same layout with
slots toggled rather than separate code paths.

Note: the resizable sidebar/content sash (a `PanedWindow`) is deferred to the
collapse step — for now the body uses fixed-width pack slots. See the build order
in `docs/_dev/appshell-navigation-spec.md`.
"""

from __future__ import annotations

import sys
from typing import Any

from bootstack._runtime.app import App
from bootstack.widgets._impl.composites.toolbar import Toolbar
from bootstack.widgets._impl.primitives.frame import Frame


# Default region sizing (pixels). Rail and compact sidebar share a width so a
# collapsed single sidebar matches the two-tier rail (the seam rule).
DEFAULT_RAIL_WIDTH = 52
DEFAULT_SIDEBAR_WIDTH = 240
DEFAULT_DOCK_WIDTH = 280


class ShellLayout(App):
    """The shell's band layout — a window of toggleable region slots.

    Args:
        title: Window title.
        theme: Theme name, or None for the default.
        size: Initial window size as `(width, height)`.
        undecorated: Remove OS chrome and draw a custom border (ignored on
            macOS). Enables window controls + dragging on the chrome row.
        rail_width: Width of the workspace rail (and compact sidebar) in pixels.
        sidebar_width: Width of the expanded sidebar in pixels.
        dock_width: Width of the detail/inspector dock in pixels.
        **kwargs: Forwarded to `App` (position, minsize, locale, etc.).
    """

    def __init__(
        self,
        *,
        title: str = "",
        theme: str | None = None,
        size: tuple[int, int] | None = None,
        undecorated: bool = False,
        rail_width: int = DEFAULT_RAIL_WIDTH,
        sidebar_width: int = DEFAULT_SIDEBAR_WIDTH,
        dock_width: int = DEFAULT_DOCK_WIDTH,
        **kwargs: Any,
    ) -> None:
        # overrideredirect has no effect on macOS — disable undecorated there.
        if sys.platform == "darwin":
            undecorated = False

        app_kwargs: dict[str, Any] = {"title": title, "override_redirect": undecorated}
        if theme is not None:
            app_kwargs["theme"] = theme
        if size is not None:
            app_kwargs["size"] = size
        app_kwargs.update(kwargs)
        super().__init__(**app_kwargs)

        self._undecorated = undecorated
        self._rail_width = rail_width
        self._sidebar_width = sidebar_width
        self._dock_width = dock_width

        # Visibility flags. Content is always shown; the rest are slots.
        self._show_chrome = False
        self._show_statusbar = False
        self._show_rail = False
        self._show_sidebar = True
        self._show_dock = False

        self._build_regions()
        self._relayout_window()
        self._relayout_body()

    # ----- Construction -----

    def _build_regions(self) -> None:
        # In undecorated mode the OS border is gone; a bordered frame substitutes
        # it (padding is required or the border is obscured by children).
        if self._undecorated:
            root = Frame(self, show_border=True, padding=1)
            root.pack(fill="both", expand=True)
        else:
            root = self
        # NB: do not name this `self._root` — tkinter's `Misc._root()` is a
        # method; shadowing it with an attribute breaks event dispatch.
        self._region_root = root

        # Full-width bands.
        self._chrome = Frame(root)
        self._statusbar = Toolbar(root, surface="chrome", draggable=False)

        # Body row + its slots.
        self._body = Frame(root)
        self._rail = Frame(self._body, surface="chrome")
        self._sidebar = Frame(self._body, surface="card")
        self._content = Frame(self._body)
        self._dock = Frame(self._body, surface="card")

        # Fixed-width slots keep their requested width instead of shrinking to
        # fit their children.
        for frame, width in (
            (self._rail, self._rail_width),
            (self._sidebar, self._sidebar_width),
            (self._dock, self._dock_width),
        ):
            frame.configure(width=width)
            frame.pack_propagate(False)

    # ----- Layout (re-pack in canonical order on every visibility change) -----

    def _relayout_window(self) -> None:
        """Re-pack the full-width bands and the body in canonical order."""
        for child in (self._chrome, self._statusbar, self._body):
            child.pack_forget()
        if self._show_chrome:
            self._chrome.pack(side="top", fill="x")
        if self._show_statusbar:
            self._statusbar.pack(side="bottom", fill="x")
        # Body fills whatever the bands leave; packed last so it claims the middle.
        self._body.pack(side="top", fill="both", expand=True)

    def _relayout_body(self) -> None:
        """Re-pack the body slots left-to-right in canonical order."""
        for child in (self._rail, self._sidebar, self._content, self._dock):
            child.pack_forget()
        if self._show_rail:
            self._rail.pack(side="left", fill="y")
        if self._show_sidebar:
            self._sidebar.pack(side="left", fill="y")
        self._content.pack(side="left", fill="both", expand=True)
        if self._show_dock:
            self._dock.pack(side="right", fill="y")

    # ----- Region visibility -----

    def set_chrome_visible(self, visible: bool) -> None:
        """Show or hide the top chrome band."""
        if self._show_chrome != visible:
            self._show_chrome = visible
            self._relayout_window()

    def set_statusbar_visible(self, visible: bool) -> None:
        """Show or hide the bottom status band."""
        if self._show_statusbar != visible:
            self._show_statusbar = visible
            self._relayout_window()

    def set_rail_visible(self, visible: bool) -> None:
        """Show or hide the workspace rail."""
        if self._show_rail != visible:
            self._show_rail = visible
            self._relayout_body()

    def set_sidebar_visible(self, visible: bool) -> None:
        """Show or hide the sidebar slot."""
        if self._show_sidebar != visible:
            self._show_sidebar = visible
            self._relayout_body()

    def set_dock_visible(self, visible: bool) -> None:
        """Show or hide the detail/inspector dock."""
        if self._show_dock != visible:
            self._show_dock = visible
            self._relayout_body()

    # ----- Region sizing -----

    def set_rail_width(self, width: int) -> None:
        """Set the rail width in pixels."""
        self._rail_width = width
        self._rail.configure(width=width)

    def set_sidebar_width(self, width: int) -> None:
        """Set the expanded-sidebar width in pixels."""
        self._sidebar_width = width
        self._sidebar.configure(width=width)

    def set_dock_width(self, width: int) -> None:
        """Set the dock width in pixels."""
        self._dock_width = width
        self._dock.configure(width=width)

    # ----- Region accessors -----

    @property
    def chrome(self) -> Frame:
        """The top chrome band (host for the menubar / command bar)."""
        return self._chrome

    @property
    def statusbar(self) -> Toolbar:
        """The bottom status band (a command-bar strip; passive content)."""
        return self._statusbar

    @property
    def rail(self) -> Frame:
        """The workspace rail slot."""
        return self._rail

    @property
    def sidebar(self) -> Frame:
        """The sidebar slot (the active workspace's panel)."""
        return self._sidebar

    @property
    def content(self) -> Frame:
        """The content slot (the active page)."""
        return self._content

    @property
    def dock(self) -> Frame:
        """The detail/inspector dock slot (reserved)."""
        return self._dock

    # ----- Visibility state (read-only) -----

    @property
    def chrome_visible(self) -> bool:
        """Whether the chrome band is shown."""
        return self._show_chrome

    @property
    def statusbar_visible(self) -> bool:
        """Whether the status band is shown."""
        return self._show_statusbar

    @property
    def rail_visible(self) -> bool:
        """Whether the rail is shown."""
        return self._show_rail

    @property
    def sidebar_visible(self) -> bool:
        """Whether the sidebar slot is shown."""
        return self._show_sidebar

    @property
    def dock_visible(self) -> bool:
        """Whether the dock slot is shown."""
        return self._show_dock
