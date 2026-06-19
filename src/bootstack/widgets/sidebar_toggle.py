"""SidebarToggle — a hamburger button that collapses/expands an AppShell sidebar.

This is not a standalone, place-anywhere widget like `ThemeToggle`: a sidebar
toggle only means anything in the context of one shell's sidebar. It is built by
`Toolbar.add_sidebar_toggle()` / `StatusBar.add_sidebar_toggle()`, which wire it
to the owning `AppShell`; it is not exported at the `bootstack` top level.
"""
from __future__ import annotations

from typing import Any, Literal

from bootstack.widgets.button import Button
from bootstack.widgets.types import AccentToken, ButtonVariant, WidgetDensity


class SidebarToggle(Button):
    """A hamburger button that collapses and expands an AppShell's sidebar.

    Clicking it toggles the shell's sidebar. With `collapse='compact'` (the
    default — the desktop convention) it shrinks the sidebar to an icon rail when
    that sidebar can show icons (a static `page_nav`), and falls back to fully
    hiding it when it can't (a data-bound `list_nav`/`tree_nav`). With
    `collapse='hidden'` it always toggles between hidden and expanded. Its icon
    can reflect the current state — `expand_icon` is shown while the sidebar is
    collapsed (clicking expands it) and `collapse_icon` while it is expanded
    (clicking collapses it); each falls back to `icon` when not given.

    Args:
        shell: The `AppShell` whose sidebar this controls.
        collapse: What "collapse" means — `'compact'` (shrink to the icon rail
            where possible, else hide; the default) or `'hidden'` (always fully
            hide).
        icon: Base icon, used for both states unless a state-specific icon is
            given. Defaults by mode — `'layout-sidebar'` (a panel glyph) for
            `collapse='compact'`, `'list'` (a hamburger) for `collapse='hidden'`.
        expand_icon: Icon shown while the sidebar is collapsed (the affordance to
            expand it). Falls back to `icon`.
        collapse_icon: Icon shown while the sidebar is expanded (the affordance to
            collapse it). Falls back to `icon`.
        variant: Button style variant. Default `'ghost'`.
        density: Padding density — `'default'` or `'compact'`.
        accent: Accent token applied to the icon. Defaults to the foreground.
        parent: Explicit parent widget. If omitted, the current context-stack
            container is used.
        **kwargs: Layout placement options applied by the parent container.
    """

    def __init__(
        self,
        *,
        shell: Any,
        collapse: Literal["compact", "hidden"] = "compact",
        icon: str | None = None,
        expand_icon: str | None = None,
        collapse_icon: str | None = None,
        variant: ButtonVariant = "ghost",
        density: WidgetDensity = "default",
        accent: AccentToken | str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._shell = shell
        self._collapse = collapse
        # Default glyph follows the collapse mode: a panel for the icon rail, a
        # hamburger for full hide.
        if icon is None:
            icon = "layout-sidebar" if collapse == "compact" else "list"
        self._base_icon = icon
        self._expand_icon = expand_icon
        self._collapse_icon = collapse_icon
        super().__init__(
            on_click=self._toggle,
            icon=self._state_icon(),
            variant=variant,
            density=density,
            accent=accent,
            parent=parent,
            **kwargs,
        )

        # Keep the icon matching the live sidebar state — toggling here or
        # elsewhere (Ctrl-B, another control) refreshes it. Setting the icon never
        # fires a click, so there is no cycle.
        self._subs = [
            shell.on_sidebar_toggle(self._sync_icon),
            shell.on_sidebar_mode_change(self._sync_icon),
        ]
        self.on_destroy(self._cleanup_sidebar_toggle)

    def _is_expanded(self) -> bool:
        return self._shell.sidebar_mode == "expanded"

    def _state_icon(self) -> str:
        if self._is_expanded():
            return self._collapse_icon or self._base_icon
        return self._expand_icon or self._base_icon

    def _toggle(self) -> None:
        if self._collapse == "hidden":
            # Always fully hide (VS Code-style focus collapse).
            self._shell.toggle_sidebar()
            return
        # "compact": collapse as far as is useful — to the icon rail when the
        # active sidebar can show icons, otherwise hide it (a data list can't
        # compact). Mirrors the shell's own Ctrl-B behavior.
        if self._can_compact():
            mode = self._shell.sidebar_mode
            self._shell.sidebar_mode = "expanded" if mode == "compact" else "compact"
        else:
            self._shell.toggle_sidebar()

    def _can_compact(self) -> bool:
        """Whether the active sidebar can shrink to icons (vs. only hide)."""
        try:
            return bool(self._shell._internal._can_compact_active())
        except Exception:
            return False

    def _sync_icon(self, _event: Any = None) -> None:
        self.icon = self._state_icon()

    def _cleanup_sidebar_toggle(self, _event: Any = None) -> None:
        for sub in self._subs:
            try:
                sub.cancel()
            except Exception:
                pass


__all__ = ["SidebarToggle"]
