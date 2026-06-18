"""TabView widget - a tabbed container combining Tabs with PageStack."""
from __future__ import annotations

__all__ = ['TabView']

import tkinter as tk
from typing_extensions import Unpack
from typing import Any, Callable, Literal

from bootstack.widgets._impl.primitives.frame import Frame, FrameKwargs
from bootstack.widgets._impl.composites.tabs.tabs import Tabs
from bootstack.widgets._impl.composites.tabs.tabitem import TabItem
from bootstack.events import (
    ChangeMethod, ChangeReason,
    TabActivateEvent, TabChangeEvent, TabDeactivateEvent, TabRef,
)
from bootstack.widgets._impl.composites.pagestack import PageStack
from bootstack.widgets.types import Master
from bootstack._core import NavigationError


class TabView(Frame):
    """A tabbed container that combines Tabs with a PageStack.

    TabView provides a complete tabbed interface where each tab corresponds
    to a page in the page stack. Selecting a tab navigates to the associated
    page.

    """

    def __init__(
        self,
        master: Master = None,
        orient: Literal['horizontal', 'vertical'] = 'horizontal',
        show_divider: bool = None,
        compound: Literal['left', 'right', 'top', 'bottom', 'center', 'none'] = 'left',
        tab_width: None | int | Literal['stretch'] = None,
        tab_padding: tuple = (12, 8),
        tab_anchor: str = None,
        enable_closing: bool | Literal['hover'] = False,
        enable_adding: bool = False,
        accent: str = None,
        **kwargs: Unpack[FrameKwargs]
    ):
        """Create a TabView widget.

        Args:
            master: Parent widget. If None, uses the default root window.
            orient: Orientation of the tab bar. 'horizontal' places tabs above
                the content, 'vertical' places tabs to the left. Default is 'horizontal'.
            show_divider: Whether to show a divider between tabs and content.
            compound: How to position icon relative to text in tabs.
            tab_width: Width of tabs (None, integer, or 'stretch').
            tab_padding: Padding for all tabs as (horizontal, vertical).
            tab_anchor: Anchor for tab text/icon alignment. If None, defaults
                to 'w' for vertical orientation, 'center' for horizontal.
            enable_closing: Default close button visibility for all tabs.
                True=always visible, False=hidden, 'hover'=visible on hover.
                Can be overridden per-tab via `closable` in add().
            enable_adding: If True, shows an "add" button that fires `<<TabAdd>>`.
            accent: Accent token for styling.
            **kwargs: Additional arguments passed to Frame.
        """
        super().__init__(master, **kwargs)

        self._orient = orient
        self._accent = accent

        # Create internal variable for tab selection
        self._tab_variable = tk.StringVar()

        # Create tabs container
        self._tabs = Tabs(
            self,
            orient=orient,
            show_divider=show_divider,
            compound=compound,
            tab_width=tab_width,
            tab_padding=tab_padding,
            tab_anchor=tab_anchor,
            enable_closing=enable_closing,
            enable_adding=enable_adding,
            variable=self._tab_variable,
            accent=accent,
        )

        # Create page stack
        self._page_stack = PageStack(self)

        # Layout based on orientation
        if orient == 'horizontal':
            self._tabs.pack(side='top', fill='x')
            self._page_stack.pack(side='top', fill='both', expand=True)
        else:
            self._tabs.pack(side='left', fill='y')
            self._page_stack.pack(side='left', fill='both', expand=True)

        # Track tabs by key for removal
        self._tab_map: dict[str, TabItem] = {}

        # Tab text tokens for locale retranslation — key → original text
        self._tab_locale_tokens: dict[str, str] = {}

        # Hidden tab keys (tab bar hidden, page still registered)
        self._hidden_tabs: set[str] = set()

        # Typed-event state — defaults represent a user click
        self._prev_key: str | None = None
        self._next_reason: ChangeReason = "user"
        self._next_via: ChangeMethod = "click"

        # Forward tab strip events to self so callers can bind at the TabView level
        self._tabs.bind('<<TabAdd>>', lambda e: self.event_generate('<<TabAdd>>', when='tail'), add='+')
        self._tabs.bind('<<TabClose>>', lambda e: self.event_generate('<<TabClose>>', data=getattr(e, 'data', None), when='tail'), add='+')

        # Bind variable trace to navigate pages and fire typed events
        self._trace_id = self._tab_variable.trace_add('write', self._on_tab_selected)

        # Locale retranslation
        self.winfo_toplevel().bind(
            "<<LocaleChanged>>", self._on_locale_changed, add='+'
        )

        # Clean up trace on destroy
        self.bind('<Destroy>', self._on_destroy, add='+')

    # -------------------------------------------------------------------------
    # Internal
    # -------------------------------------------------------------------------

    def _on_destroy(self, event=None):
        """Clean up variable trace when widget is destroyed."""
        if event.widget is not self:
            return
        if self._trace_id is not None:
            try:
                self._tab_variable.trace_remove('write', self._trace_id)
            except Exception:
                pass
            self._trace_id = None

    def _on_tab_selected(self, *args):
        """Handle tab selection — navigate page stack and fire typed events."""
        key = self._tab_variable.get()
        if not key or key not in self._tab_map:
            return

        prev_key = self._prev_key
        reason: ChangeReason = self._next_reason
        via: ChangeMethod = self._next_via

        # Reset to user-click defaults for the next change
        self._next_reason = "user"
        self._next_via = "click"

        if key == prev_key:
            return

        # Navigate page stack
        current_page = self._page_stack.current()
        if current_page is None or current_page[0] != key:
            self._page_stack.navigate(key)

        # Build typed event payload
        def _tab_ref(k: str) -> TabRef:
            return TabRef(key=k, text=self._tab_locale_tokens.get(k, k))

        current_ref = _tab_ref(key)
        previous_ref = _tab_ref(prev_key) if prev_key else None

        payload = TabChangeEvent(
            current=current_ref,
            previous=previous_ref,
            reason=reason,
            via=via,
        )

        self.event_generate('<<TabChanged>>', data=payload, when='tail')

        # Per-tab lifecycle events
        if prev_key and prev_key in self._tab_map:
            deactivate = TabDeactivateEvent(
                key=prev_key,
                text=self._tab_locale_tokens.get(prev_key, prev_key),
            )
            self.event_generate('<<TabDeactivate>>', data=deactivate, when='tail')

        activate = TabActivateEvent(
            key=key,
            text=self._tab_locale_tokens.get(key, key),
        )
        self.event_generate('<<TabActivate>>', data=activate, when='tail')

        self._prev_key = key

    def _on_locale_changed(self, _event=None):
        """Retranslate all tab labels when the locale changes."""
        try:
            from bootstack.i18n import MessageCatalog
        except ImportError:
            return
        for key, token in self._tab_locale_tokens.items():
            if key in self._tab_map:
                translated = MessageCatalog.translate(token)
                self._tab_map[key].configure(text=translated)

    def _set_next_change(self, reason: ChangeReason, via: ChangeMethod) -> None:
        """Tag the next variable change with the given reason and method."""
        self._next_reason = reason
        self._next_via = via

    # -------------------------------------------------------------------------
    # Public API — tab management
    # -------------------------------------------------------------------------

    def add(
        self,
        key: str,
        text: str = "",
        icon: str | dict = None,
        page: tk.Widget = None,
        closable: bool | Literal['hover'] | None = None,
        close_command: Callable = None,
        command: Callable = None,
        **kwargs
    ) -> tk.Widget:
        """Add a tab and its associated page.

        Args:
            key: Unique identifier for the tab/page.
            text: Text to display on the tab.
            icon: Icon to display on the tab.
            page: The page widget. If None, creates a Frame.
            closable: Close button visibility (True, False, 'hover', or None).
                If None, uses the widget's `enable_closing` setting.
            close_command: Callback when close button is clicked.
                If not provided and closable is enabled, removes the tab/page.
            command: Callback when tab is selected.
            **kwargs: Additional arguments passed to page Frame (if created).

        Returns:
            The page widget.
        """
        effective_closable = closable if closable is not None else self._tabs._enable_closing

        if effective_closable and close_command is None:
            close_command = lambda k=key: self.forget_tab(k)

        tab = self._tabs.add(
            text=text,
            icon=icon,
            key=key,
            value=key,
            closable=closable,
            close_command=close_command,
            command=command,
        )
        self._tab_map[key] = tab
        self._tab_locale_tokens[key] = text

        page_widget = self._page_stack.add(key, page, **kwargs)

        if len(self._tab_map) == 1:
            self._set_next_change("api", "programmatic")
            self._tab_variable.set(key)

        return page_widget

    def __getitem__(self, key: str) -> tk.Widget:
        """Return the page widget for *key*.

        Args:
            key: Tab/page identifier.

        Returns:
            The page widget registered under *key*.

        Raises:
            KeyError: If no tab with the given key exists.
        """
        return self._page_stack.item(key)

    def select(self, key: str) -> None:
        """Select a tab by its key.

        Args:
            key: The identifier of the tab to select.

        Raises:
            NavigationError: If no tab with the given key exists.
        """
        if key not in self._tab_map:
            raise NavigationError(f"No tab with key '{key}'")
        if key in self._hidden_tabs:
            return
        self._set_next_change("api", "programmatic")
        self._tab_variable.set(key)

    def navigate(self, key: str, data: dict = None) -> None:
        """Navigate to a tab/page with optional data.

        Args:
            key: The identifier of the tab/page to navigate to.
            data: Optional data to pass to the page.

        Raises:
            NavigationError: If no tab with the given key exists.
        """
        if key not in self._tab_map:
            raise NavigationError(f"No tab with key '{key}'")
        if key in self._hidden_tabs:
            return
        self._set_next_change("api", "programmatic")
        self._tab_variable.set(key)
        if data:
            self._page_stack.navigate(key, data=data)

    def hide_tab(self, key: str) -> None:
        """Hide a tab without removing it from the registry.

        The tab disappears from the bar but remains registered. Restore it
        with `show_tab()`. If the hidden tab was selected, the next
        available visible tab is selected automatically.

        Args:
            key: The identifier of the tab to hide.

        Raises:
            NavigationError: If no tab with the given key exists.
        """
        if key not in self._tab_map:
            raise NavigationError(f"No tab with key '{key}'")
        if key in self._hidden_tabs:
            return

        self._hidden_tabs.add(key)
        self._tabs.hide(key)

        if self._tab_variable.get() == key:
            next_key = self._next_visible_key(exclude=key)
            if next_key:
                self._set_next_change("hide", "programmatic")
                self._tab_variable.set(next_key)
            else:
                self._tab_variable.set('')
                self._prev_key = None

    def show_tab(self, key: str) -> None:
        """Restore a previously hidden tab to the bar.

        Args:
            key: The identifier of the tab to show.

        Raises:
            NavigationError: If no tab with the given key exists.
        """
        if key not in self._tab_map:
            raise NavigationError(f"No tab with key '{key}'")
        self._hidden_tabs.discard(key)
        self._tabs.show(key)

    def forget_tab(self, key: str) -> None:
        """Remove a tab and its page entirely.

        Unlike `hide_tab()`, the tab is unregistered and cannot be restored.
        If the removed tab was selected, the next available tab is selected.

        Args:
            key: The identifier of the tab/page to remove.

        Raises:
            NavigationError: If no tab with the given key exists.
        """
        if key not in self._tab_map:
            raise NavigationError(f"No tab with key '{key}'")

        was_selected = self._tab_variable.get() == key

        tab = self._tab_map.pop(key)
        self._tab_locale_tokens.pop(key, None)
        self._hidden_tabs.discard(key)
        self._tabs.remove(key)
        tab.destroy()

        self._page_stack.remove(key)

        if was_selected:
            next_key = self._next_visible_key()
            if next_key:
                self._set_next_change("forget", "programmatic")
                self._tab_variable.set(next_key)
            else:
                self._tab_variable.set('')
                self._prev_key = None

    def remove(self, key: str) -> None:
        """Remove a tab and its associated page.

        Alias for `forget_tab()`.

        Args:
            key: The identifier of the tab/page to remove.
        """
        self.forget_tab(key)

    def _next_visible_key(self, exclude: str | None = None) -> str | None:
        """Return the first visible (non-hidden) tab key, skipping *exclude*."""
        for k in self._tab_map:
            if k != exclude and k not in self._hidden_tabs:
                return k
        return None

    # -------------------------------------------------------------------------
    # Introspection
    # -------------------------------------------------------------------------

    @property
    def tabs_widget(self) -> Tabs:
        """Get the internal Tabs widget."""
        return self._tabs

    @property
    def page_stack_widget(self) -> PageStack:
        """Get the internal PageStack widget."""
        return self._page_stack

    @property
    def current(self) -> str | None:
        """Get the currently selected tab key."""
        key = self._tab_variable.get()
        return key if key else None

    def page(self, key: str) -> tk.Widget:
        """Get a page widget by its key.

        Args:
            key: The identifier of the page.

        Returns:
            The page widget.

        Raises:
            KeyError: If no page with the given key exists.
        """
        return self._page_stack.item(key)

    def pages(self) -> tuple[tk.Widget, ...]:
        """Get all page widgets.

        Returns:
            A tuple of all page widgets.
        """
        return self._page_stack.items()

    def page_keys(self) -> tuple[str, ...]:
        """Get all page keys.

        Returns:
            A tuple of all page keys.
        """
        return self._page_stack.keys()

    def tab(self, key: str) -> TabItem:
        """Get a TabItem by its key.

        Args:
            key: The identifier of the tab.

        Returns:
            The TabItem widget.

        Raises:
            KeyError: If no tab with the given key exists.
        """
        if key not in self._tab_map:
            raise NavigationError(f"No tab with key '{key}'")
        return self._tab_map[key]

    def tabs(self) -> tuple[TabItem, ...]:
        """Get all TabItem widgets.

        Returns:
            A tuple of all TabItem widgets in the order they were added.
        """
        return tuple(self._tab_map.values())

    def tab_keys(self) -> tuple[str, ...]:
        """Get all tab keys.

        Returns:
            A tuple of all tab keys in the order they were added.
        """
        return tuple(self._tab_map.keys())

    def keys(self) -> tuple[str, ...]:
        """Get all tab keys.

        Alias for `tab_keys()`.

        Returns:
            A tuple of all tab keys in the order they were added.
        """
        return self.tab_keys()

    def configure_tab(self, key: str, option: str | None = None, **kwargs: Unpack[FrameKwargs]):
        """Configure a specific tab by its key.

        Args:
            key: The key of the tab to configure.
            option: If provided, return the value of this option.
            **kwargs: Configuration options to apply to the tab.

        Returns:
            If option is provided, returns the value of that option.
        """
        tab = self.tab(key)
        if option is not None:
            return tab.cget(option)
        tab.configure(**kwargs)

    # -------------------------------------------------------------------------
    # Events
    # -------------------------------------------------------------------------

    def on_page_changed(self, callback: Callable) -> str:
        """Register a callback for `<<PageChange>>` events.

        Args:
            callback: Receives `event.data` with navigation info: `page`,
                `prev_page`, `nav`, `index`, `length`, `can_back`, `can_forward`.

        Returns:
            Bind ID — pass to `off_page_changed()` to unsubscribe.
        """
        return self._page_stack.on_page_changed(callback)

    def off_page_changed(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<PageChange>>`.

        Args:
            bind_id: ID returned by `on_page_changed()`. If None, removes all.
        """
        self._page_stack.off_page_changed(bind_id)

    def on_tab_added(self, callback: Callable) -> str:
        """Register a callback for `<<TabAdd>>` events (fires when the add button is clicked).

        Args:
            callback: Called when the add button is clicked. `event.data` is None.

        Returns:
            Bind ID — pass to `off_tab_added()` to unsubscribe.
        """
        return self._tabs.on_tab_added(callback)

    def off_tab_added(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<TabAdd>>`.

        Args:
            bind_id: ID returned by `on_tab_added()`. If None, removes all.
        """
        self._tabs.off_tab_added(bind_id)

    def on_tab_changed(self, callback: Callable[[TabChangeEvent], None]) -> str:
        """Register a callback for `<<TabChanged>>` events.

        Args:
            callback: Receives a `TabChangeEvent` payload with attributes
                `current` (`TabRef`), `previous` (`TabRef | None`),
                `reason` (`ChangeReason`), and `via` (`ChangeMethod`).

        Returns:
            Bind ID — pass to `off_tab_changed()` to unsubscribe.
        """
        return self.bind('<<TabChanged>>', callback, add='+')

    def off_tab_changed(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<TabChanged>>`.

        Args:
            bind_id: ID returned by `on_tab_changed()`. If None, removes all.
        """
        self.unbind('<<TabChanged>>', bind_id)

    def on_tab_activated(self, callback: Callable[[TabActivateEvent], None]) -> str:
        """Register a callback for `<<TabActivate>>` events.

        Fires when a tab becomes the selected (active) tab.

        Args:
            callback: Receives a `TabActivateEvent` payload with attributes
                `key` and `text`.

        Returns:
            Bind ID — pass to `off_tab_activated()` to unsubscribe.
        """
        return self.bind('<<TabActivate>>', callback, add='+')

    def off_tab_activated(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<TabActivate>>`.

        Args:
            bind_id: ID returned by `on_tab_activated()`. If None, removes all.
        """
        self.unbind('<<TabActivate>>', bind_id)

    def on_tab_deactivated(self, callback: Callable[[TabDeactivateEvent], None]) -> str:
        """Register a callback for `<<TabDeactivate>>` events.

        Fires when a tab stops being the selected (active) tab.

        Args:
            callback: Receives a `TabDeactivateEvent` payload with attributes
                `key` and `text`.

        Returns:
            Bind ID — pass to `off_tab_deactivated()` to unsubscribe.
        """
        return self.bind('<<TabDeactivate>>', callback, add='+')

    def off_tab_deactivated(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<TabDeactivate>>`.

        Args:
            bind_id: ID returned by `on_tab_deactivated()`. If None, removes all.
        """
        self.unbind('<<TabDeactivate>>', bind_id)

    def on_tab_closed(self, callback: Callable) -> str:
        """Register a callback for `<<TabClose>>` events (fires when a tab's close button is clicked).

        Args:
            callback: Receives `event.data = {'value': Any}` — the closed tab's value.

        Returns:
            Bind ID — pass to `off_tab_closed()` to unsubscribe.
        """
        return self._tabs.on_tab_closed(callback)

    def off_tab_closed(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<TabClose>>`.

        Args:
            bind_id: ID returned by `on_tab_closed()`. If None, removes all.
        """
        self._tabs.off_tab_closed(bind_id)
