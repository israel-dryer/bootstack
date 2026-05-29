from __future__ import annotations

import tkinter
from typing import Any, Callable, Literal

from bootstack.widgets.composites.tabs.tabview import TabView as _InternalTabView
from bootstack.widgets.composites.tabs.events import TabChangeEventData, TabRef
from bootstack.widgets.public.base import PublicWidgetBase
from bootstack.widgets.public.container import PACK_KEYS
from bootstack.widgets.public.context import push_container, pop_container
from bootstack.widgets.public.events import register_widget_events, resolve_event
from bootstack.widgets.public.subscription import Subscription

_TABS_EVENTS: dict[str, str] = {
    "change":    "<<TabChanged>>",
    "tab_close": "<<TabClose>>",
    "tab_add":   "<<TabAdd>>",
}


class _TabPage:
    """Context-manager for placing children inside a tab's page frame."""

    def __init__(self, page_widget: tkinter.Widget) -> None:
        self._page = page_widget

    def _child_master(self) -> tkinter.Widget:
        return self._page

    def guide_layout(self, child: PublicWidgetBase, **layout_kw: Any) -> None:
        options = {k: v for k, v in layout_kw.items() if k in PACK_KEYS}
        child._internal.pack(in_=self._page, **options)

    def __enter__(self) -> "_TabPage":
        push_container(self)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pop_container(self)


class Tabs(PublicWidgetBase):
    """A tabbed container. Add pages with `.add()` and place children inside them.

    Usage::

        tabs = bs.Tabs()
        with tabs.add("home", text="Home"):
            bs.Label("Welcome")
        with tabs.add("settings", text="Settings"):
            bs.Label("Settings here")

    Args:
        orient: `'horizontal'` (default, tabs above content) or `'vertical'` (tabs left).
        show_divider: Show a divider line between the tab bar and the page area.
        tab_width: Fixed tab width in pixels, `'stretch'` to fill available space, or
            `None` (default, size to content).
        allow_close: Show close buttons on tabs. `True` = always, `False` = never,
            `'hover'` = on hover. Default `False`.
        allow_add: Show an add-tab button that fires the `tab_add` event.
        accent: Accent token for the tab bar.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        *,
        orient: Literal["horizontal", "vertical"] = "horizontal",
        show_divider: bool | None = None,
        tab_width: int | Literal["stretch"] | None = None,
        allow_close: bool | Literal["hover"] = False,
        allow_add: bool = False,
        accent: str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "orient": orient,
            "enable_closing": allow_close,
            "enable_adding": allow_add,
        }
        if show_divider is not None:
            internal_kwargs["show_divider"] = show_divider
        if tab_width is not None:
            internal_kwargs["tab_width"] = tab_width
        if accent is not None:
            internal_kwargs["accent"] = accent
        internal_kwargs.update(kwargs)

        self._internal = _InternalTabView(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Event routing -----

    def on(self, event: str, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Bind `handler` to `event` and return a `Subscription`."""
        sequence = resolve_event(self, str(event))
        # <<TabAdd>> and <<TabClose>> are generated on the internal Tabs bar widget,
        # not on the TabView frame itself.
        if sequence in ("<<TabAdd>>", "<<TabClose>>"):
            target = self._internal._tabs
        else:
            target = self._internal
        bind_id = target.bind(sequence, handler, add="+")
        return Subscription(target, sequence, bind_id)

    # ----- Tab management -----

    def add(
        self,
        key: str,
        *,
        label: str = "",
        icon: str | None = None,
        closable: bool | Literal["hover"] | None = None,
        close_command: Callable | None = None,
    ) -> _TabPage:
        """Add a tab and return a context manager for placing its children.

        Usage::

            with tabs.add("home", label="Home"):
                bs.Label("Content goes here")

        Args:
            key: Unique identifier for the tab/page.
            label: Label displayed on the tab.
            icon: Icon name displayed on the tab.
            closable: Close-button visibility for this tab. Overrides `enable_closing`.
            close_command: Called when the close button is clicked. Defaults to
                removing the tab via `forget_tab()`.

        Returns:
            `_TabPage` — use as a context manager to place children.
        """
        add_kwargs: dict[str, Any] = {}
        if icon is not None:
            add_kwargs["icon"] = icon
        if closable is not None:
            add_kwargs["closable"] = closable
        if close_command is not None:
            add_kwargs["close_command"] = close_command

        page_widget = self._internal.add(key, text=label, **add_kwargs)
        return _TabPage(page_widget)

    def select(self, key: str) -> None:
        """Select the tab identified by `key`."""
        self._internal.select(key)

    def hide_tab(self, key: str) -> None:
        """Hide a tab without removing it. Restore with `show_tab()`."""
        self._internal.hide_tab(key)

    def show_tab(self, key: str) -> None:
        """Restore a previously hidden tab."""
        self._internal.show_tab(key)

    def forget_tab(self, key: str) -> None:
        """Remove a tab and its page entirely."""
        self._internal.forget_tab(key)

    # ----- Properties / introspection -----

    @property
    def current(self) -> str | None:
        """Key of the currently selected tab, or `None` if no tab is selected."""
        return self._internal.current

    def tab_keys(self) -> tuple[str, ...]:
        """All tab keys in insertion order."""
        return self._internal.tab_keys()

    def page_keys(self) -> tuple[str, ...]:
        """All page keys in insertion order."""
        return self._internal.page_keys()

    # ----- Event shorthands -----

    def on_change(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired when the selected tab changes.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("change", handler)

    def on_tab_close(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired when a tab's close button is clicked.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("tab_close", handler)

    def on_tab_add(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired when the add-tab button is clicked.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("tab_add", handler)


register_widget_events(Tabs, _TABS_EVENTS)

__all__ = ["Tabs", "TabChangeEventData", "TabRef"]