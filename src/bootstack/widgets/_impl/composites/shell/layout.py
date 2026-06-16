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
from bootstack.widgets._impl.primitives.packframe import PackFrame
from bootstack.widgets._impl.primitives.separator import Separator


# Default region sizing (pixels). Rail and compact sidebar share a width so a
# collapsed single sidebar matches the two-tier rail (the seam rule).
DEFAULT_RAIL_WIDTH = 52
DEFAULT_SIDEBAR_WIDTH = 240
DEFAULT_DOCK_WIDTH = 280

# Region surfaces — the single source of truth. Nav items blend their selection
# tint (and round their corners) against the SAME surface they render on, so the
# color can never mismatch the background; callers thread these down rather than
# hardcoding a surface token independently.
#
# Elevation tiers: the rail is the chrome tier; the sidebar (and dock) sit on a
# SUBTLE `raised` elevation (half the `card` step) — gentle, not a big ramp, and
# reinforced by the dividers. Selection is neutral, so a subtle elevation no
# longer washes it out. content < raised < chrome.
RAIL_SURFACE = "chrome"
SIDEBAR_SURFACE = "raised"
DOCK_SURFACE = "raised"
STATUSBAR_SURFACE = "chrome"

# Divider stroke softness. The default separator border blends 16% toward the
# surface's on-color (text), which reads strong on the near-black dark surfaces;
# the shell's region dividers blend less (closer to the surface) for a quieter
# hairline. Higher = quieter.
DIVIDER_BORDER_STRENGTH = 0.90


class ShellLayout(App):
    """The shell's band layout — a window of toggleable region slots.

    Args:
        title: Window title.
        theme: Theme name, or None for the default.
        size: Initial window size as `(width, height)`.
        undecorated: Remove OS chrome and draw a custom border (ignored on
            macOS). Build the title bar yourself with
            `add_toolbar(show_window_controls=True)` — the framework adds no
            chrome of its own.
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
        chrome_surface: str = "chrome",
        rail_surface: str = RAIL_SURFACE,
        sidebar_surface: str = SIDEBAR_SURFACE,
        statusbar_surface: str = STATUSBAR_SURFACE,
        **kwargs: Any,
    ) -> None:
        # overrideredirect has no effect on macOS — disable undecorated there.
        if sys.platform == "darwin":
            undecorated = False

        self._chrome_surface = chrome_surface
        self._rail_surface = rail_surface
        self._sidebar_surface = sidebar_surface
        self._statusbar_surface = statusbar_surface
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

        # Visibility flags. Content is always shown; the rest are slots. The
        # chrome band stays lazy (menus / command bar only); a custom title bar
        # in undecorated mode is just an `add_toolbar(show_window_controls=True)`.
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

        # Full-width top and bottom bands. The menu / command bar belongs at the
        # very top spanning the whole window width (the natural desktop place for
        # it); the rail + sidebar + content all sit BELOW it, in the body row.
        # The chrome band takes the chrome surface (otherwise the band shows its
        # default content surface around a menu strip that doesn't fill the row).
        # Both the chrome and status hairlines span the FULL window width (the
        # VS Code convention — the band edges run the whole way across, the rail
        # included), so they live at the window level above/below the body.
        # The stacked-toolbar region (the `add_toolbar()` host) sits at the very
        # top of the shell, above the chrome band and body. Chrome-surfaced so any
        # gap (e.g. a divider margin) reads chrome, not the content surface.
        self._toolbar_stack = PackFrame(root, direction="vertical", surface="chrome")
        self._chrome = Frame(root, surface=self._chrome_surface)
        self._chrome_sep = Separator(root, orient="horizontal", border_strength=DIVIDER_BORDER_STRENGTH)
        self._statusbar = Toolbar(root, surface=self._statusbar_surface, draggable=False)
        self._status_sep = Separator(root, orient="horizontal", border_strength=DIVIDER_BORDER_STRENGTH)

        # Body row + its slots.
        self._body = Frame(root)
        self._rail = Frame(self._body, surface=self._rail_surface)
        # A thin divider between the rail and the sidebar reinforces the tier
        # boundary (shown only when the rail renders). Each divider takes the
        # surface of the region it edges so its stroke is derived against that
        # surface, not the default content surface.
        self._rail_sep = Separator(self._body, orient="vertical", surface=self._rail_surface,
                                   border_strength=DIVIDER_BORDER_STRENGTH)
        self._sidebar = Frame(self._body, surface=self._sidebar_surface)
        # A matching divider on the sidebar's right edge defines the sidebar/
        # content boundary (shown only when the sidebar is visible).
        self._sidebar_sep = Separator(self._body, orient="vertical", surface=self._sidebar_surface,
                                      border_strength=DIVIDER_BORDER_STRENGTH)
        self._content = Frame(self._body)
        self._dock = Frame(self._body, surface=DOCK_SURFACE)

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
        """Re-pack the full-width toolbar / chrome / status bands and the body."""
        for child in (self._toolbar_stack, self._chrome, self._chrome_sep,
                      self._status_sep, self._statusbar, self._body):
            child.pack_forget()
        # The stacked-toolbar region — full width, at the very top, above the
        # chrome band + body.
        self._toolbar_stack.pack(side="top", fill="x")
        if self._show_chrome:
            self._chrome.pack(side="top", fill="x")
            self._chrome_sep.pack(side="top", fill="x")
        if self._show_statusbar:
            # Band at the very bottom; its hairline just above it (both full width).
            self._statusbar.pack(side="bottom", fill="x")
            self._status_sep.pack(side="bottom", fill="x")
        # Body fills whatever the bands leave; packed last so it claims the middle.
        self._body.pack(side="top", fill="both", expand=True)

    def _relayout_body(self) -> None:
        """Re-pack the rail / sidebar / content / dock slots left-to-right."""
        for child in (self._rail, self._rail_sep, self._sidebar, self._sidebar_sep,
                      self._content, self._dock):
            child.pack_forget()
        if self._show_rail:
            self._rail.pack(side="left", fill="y")
            self._rail_sep.pack(side="left", fill="y")
        if self._show_sidebar:
            self._sidebar.pack(side="left", fill="y")
            self._sidebar_sep.pack(side="left", fill="y")
        self._content.pack(side="left", fill="both", expand=True)
        if self._show_dock:
            self._dock.pack(side="right", fill="y")

    # ----- Region visibility -----

    def set_chrome_visible(self, visible: bool) -> None:
        """Show or hide the top chrome band (and its full-width hairline)."""
        if self._show_chrome != visible:
            self._show_chrome = visible
            self._relayout_window()

    def set_statusbar_visible(self, visible: bool) -> None:
        """Show or hide the bottom status band (and its full-width hairline)."""
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
    def toolbar_stack(self) -> PackFrame:
        """The vertical region hosting `add_toolbar()` toolbars (top of window)."""
        return self._toolbar_stack

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
    def sidebar_surface(self) -> str:
        """Surface token the sidebar region renders on (for matched nav tints)."""
        return self._sidebar_surface

    @property
    def rail_surface(self) -> str:
        """Surface token the rail region renders on."""
        return self._rail_surface

    @property
    def statusbar_surface(self) -> str:
        """Surface token the status band renders on."""
        return self._statusbar_surface

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
