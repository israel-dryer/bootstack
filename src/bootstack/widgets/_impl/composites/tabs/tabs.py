"""Tabs widget - a tab bar container for TabItem widgets."""
from __future__ import annotations

__all__ = ['Tabs']

import tkinter as tk
from tkinter import Variable
from typing_extensions import Unpack
from typing import Any, Callable, Literal, TYPE_CHECKING

from bootstack.widgets._impl.primitives.packframe import PackFrame
from bootstack.widgets._impl.primitives.frame import Frame, FrameKwargs
from bootstack.widgets._impl.primitives.separator import Separator
from bootstack.widgets._impl.primitives.button import Button
from bootstack.widgets._impl.composites.scrollview import ScrollView
from bootstack.widgets._impl.composites.tabs.tabitem import TabItem
from bootstack.widgets._impl.mixins.configure_mixin import configure_delegate
from bootstack.widgets.types import Master
from bootstack._core import NavigationError

if TYPE_CHECKING:
    from bootstack.signals import Signal


class Tabs(Frame):
    """A container widget for grouping TabItem widgets.

    Tabs provides a tab bar with optional divider. It manages the layout,
    orientation, and styling of child TabItems.

    Attributes:
        orient: The orientation of the tab bar ('horizontal' or 'vertical').
    """

    def __init__(
        self,
        master: Master = None,
        orient: Literal['horizontal', 'vertical'] = 'horizontal',
        variant: Literal['bar'] = 'bar',
        show_divider: bool = None,
        compound: Literal['left', 'right', 'top', 'bottom', 'center', 'none'] = 'left',
        tab_width: None | int | Literal['stretch'] = None,
        tab_min_width: int = 80,
        tab_padding: tuple = (12, 8),
        tab_anchor: str = None,
        overflow: Literal['scroll', 'clip'] = 'scroll',
        enable_closing: bool | Literal['hover'] = False,
        enable_adding: bool = False,
        max_tabs: int | None = None,
        variable: Variable = None,
        signal: 'Signal[Any]' = None,
        accent: str = None,
        **kwargs: Unpack[FrameKwargs]
    ):
        """Create a Tabs widget.

        Args:
            master: Parent widget. If None, uses the default root window.
            orient: Orientation of the tab bar. 'horizontal' places tabs in a row,
                'vertical' places tabs in a column. Default is 'horizontal'.
            variant: Visual style variant. Only 'bar' is supported.
            show_divider: Whether to show a divider line. If None (default),
                automatically set to True for 'bar' variant, False for others.
            compound: How to position icon relative to text in tabs.
                Passed to all TabItems. Default is 'left'.
            tab_width: Width of tabs. None for auto-sizing, an integer for
                fixed character width, or 'stretch' to expand tabs to fill
                available space (horizontal only). Default is None.
            tab_min_width: Minimum tab width in pixels. Tabs will not shrink
                below this value regardless of label content. Default is 80.
            tab_padding: Padding for all tabs as (horizontal, vertical).
                Default is (12, 8).
            tab_anchor: Anchor for tab text/icon alignment. If None, defaults
                to 'w' for vertical orientation, 'center' for horizontal.
            overflow: How to handle tabs that exceed the strip's length.
                'scroll' (default) keeps the tabs in a single scrolling line
                (no scrollbar; the wheel scrolls along the strip) with a
                trailing chevron button that lists the off-screen tabs and
                scrolls the chosen one into view. 'clip' keeps the legacy
                behavior (tabs past the edge are clipped). Ignored when
                `tab_width='stretch'` (tabs always fit). Applies to both
                horizontal (scrolls left/right) and vertical (scrolls
                up/down) orientations.
            enable_closing: Default close button visibility for all tabs.
                True=always visible, False=hidden, 'hover'=visible on hover.
                Can be overridden per-tab via `closable` in add_tab().
            enable_adding: If True, shows an "add" button. In horizontal
                orientation, shows a plus icon on the right. In vertical
                orientation, shows "New Tab" at the bottom. Fires `<<TabAdd>>`
                event when clicked.
            max_tabs: Maximum number of tabs allowed. When the tab count
                reaches this value the add button is disabled (and re-enabled
                when a tab is removed). None (default) means no limit.
            variable: Tk variable for tracking selected tab value.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            signal: Reactive Signal for tracking selected tab value.
            accent: Accent token for styling tabs.
            **kwargs: Additional arguments passed to Frame.
        """
        super().__init__(master=master, **kwargs)

        self._orient = orient
        self._variant = variant
        self._compound = compound
        self._tab_width = tab_width
        self._tab_min_width = tab_min_width
        self._tab_padding = tab_padding
        self._enable_closing = enable_closing
        self._enable_adding = enable_adding
        self._max_tabs = max_tabs
        self._accent = accent

        # Handle variable/signal setup
        if signal is not None:
            # Signal provided - extract its variable
            self._signal = signal
            self._variable = signal.var
        elif variable is not None:
            # Variable provided - wrap in Signal
            from bootstack.signals import Signal
            self._variable = variable
            self._signal = Signal.from_variable(variable)
        else:
            # Neither provided - create internal variable and signal
            from bootstack.signals import Signal
            self._variable = tk.StringVar()
            self._signal = Signal.from_variable(self._variable)

        # Default anchor based on orientation
        if tab_anchor is None:
            self._tab_anchor = 'w' if orient == 'vertical' else 'center'
        else:
            self._tab_anchor = tab_anchor

        # Determine show_divider default based on variant
        if show_divider is None:
            self._show_divider = variant == 'bar'
        else:
            self._show_divider = show_divider

        # Set direction based on orient
        direction = 'horizontal' if orient == 'horizontal' else 'vertical'

        # Gap between tabs
        gap = 0

        # Internal divider widget
        self._divider: Separator | None = None

        # Internal add button
        self._add_button: Button | None = None

        # Tab tracking by key
        self._tabs: dict[str, TabItem] = {}
        self._tab_order: list[str] = []
        self._tab_values: dict[str, Any] = {}
        self._tab_icons: dict[str, Any] = {}
        self._hidden: set[str] = set()
        self._counter = 0  # For auto-generating keys

        # Overflow handling. Only meaningful when tabs are content-sized;
        # 'stretch' always fits, so it disables scrolling.
        self._overflow = overflow
        self._scrollable = overflow == 'scroll' and tab_width != 'stretch'
        self._axis = 'x' if orient == 'horizontal' else 'y'
        self._scroll: ScrollView | None = None
        self._strip_row: Frame | None = None
        self._overflow_button: Button | None = None
        self._overflow_menu = None
        self._overflow_visible = False
        self._overflow_after: str | None = None
        self._canvas_cross = 0
        self._wheel_tag = f'TabStripWheel_{id(self)}'

        # Build the tab strip (scrollable or static) + divider
        if self._scrollable:
            self._build_scrollable_strip(orient, direction, gap)
        else:
            self._build_static_strip(orient, direction, gap)

        # Create add button if enabled (must be after the strip is built)
        if enable_adding:
            self._create_add_button()

        # Wire scroll behavior once everything exists
        if self._scrollable:
            self._setup_wheel_bindings()
            self._signal.subscribe(self._on_selection_scroll)
            self.bind('<Destroy>', self._on_overflow_destroy, add='+')

    def _build_static_strip(self, orient: str, direction: str, gap: int) -> None:
        """Build the legacy non-scrolling tab strip (tabs may clip)."""
        self._tab_bar = PackFrame(self, direction=direction, gap=gap)
        if orient == 'horizontal':
            self._tab_bar.pack(side='top', fill='x')
            if self._show_divider:
                self._divider = Separator(self, orient='horizontal')
                self._divider.pack(side='top', fill='x')
        else:
            self._tab_bar.pack(side='left', fill='y')
            if self._show_divider:
                self._divider = Separator(self, orient='vertical')
                self._divider.pack(side='left', fill='y')

    def _build_scrollable_strip(self, orient: str, direction: str, gap: int) -> None:
        """Build a scrollbar-less scrolling strip with a trailing overflow menu.

        The tab `PackFrame` lives inside a `ScrollView`; the add and overflow
        buttons are pinned outside the scroll region (right edge for horizontal,
        bottom for vertical) so they stay reachable while the tabs scroll.
        """
        if orient == 'horizontal':
            self._strip_row = Frame(self)
            self._strip_row.pack(side='top', fill='x')
            self._scroll = ScrollView(
                self._strip_row,
                scroll_direction='horizontal',
                scrollbar_visibility='never',
            )
            # Small gap between the scrolling tabs and the pinned add/overflow buttons.
            self._scroll.pack(side='left', fill='x', expand=True, padx=(0, 6))
        else:
            self._strip_row = Frame(self)
            self._strip_row.pack(side='left', fill='y')
            self._scroll = ScrollView(
                self._strip_row,
                scroll_direction='vertical',
                scrollbar_visibility='never',
            )
            # Small gap between the scrolling tabs and the pinned add/overflow buttons.
            self._scroll.pack(side='top', fill='y', expand=True, pady=(0, 6))

        self._tab_bar = PackFrame(self._scroll.canvas, direction=direction, gap=gap)
        self._scroll.add(self._tab_bar)

        # Match the canvas cross-size to the strip and re-evaluate overflow on
        # any size change (ScrollView's own <Configure> bindings are kept via +).
        self._tab_bar.bind('<Configure>', self._on_tabbar_configure, add='+')
        self._scroll.canvas.bind('<Configure>', self._on_viewport_configure, add='+')

        if self._show_divider:
            if orient == 'horizontal':
                self._divider = Separator(self, orient='horizontal')
                self._divider.pack(side='top', fill='x')
            else:
                self._divider = Separator(self, orient='vertical')
                self._divider.pack(side='left', fill='y')

    def _create_divider(self):
        """Create the divider separator widget."""
        if self._divider is not None:
            return
        if self._orient == 'horizontal':
            self._divider = Separator(self, orient='horizontal')
            self._divider.pack(side='top', fill='x')
        else:
            self._divider = Separator(self, orient='vertical')
            self._divider.pack(side='left', fill='y')

    def _destroy_divider(self):
        """Remove the divider widget."""
        if self._divider is not None:
            self._divider.pack_forget()
            self._divider.destroy()
            self._divider = None

    def _create_add_button(self):
        """Create the add button widget."""
        if self._add_button is not None:
            return

        # When scrolling, the add button is pinned outside the scroll region
        # (right edge for horizontal, bottom for vertical) so it stays put.
        parent = self._strip_row if self._scrollable else self._tab_bar

        if self._orient == 'horizontal':
            self._add_button = Button(
                parent,
                icon={'name': 'plus-lg', 'size': 16},
                icon_only=True,
                variant='ghost',
                command=self._on_add_click,
            )
            if self._scrollable:
                self._add_button.pack(side='right')
            else:
                self._add_button.pack()
        else:
            # "New Tab" with plus icon
            self._add_button = Button(
                parent,
                text='New',
                icon='plus-lg',
                variant='ghost',
                padding=2,
                command=self._on_add_click,
                anchor='w',
            )
            if self._scrollable:
                self._add_button.pack(side='bottom', fill='x')
            else:
                self._add_button.pack(fill='x')

        self._update_add_button_state()

    def _destroy_add_button(self):
        """Remove the add button widget."""
        if self._add_button is not None:
            self._add_button.pack_forget()
            self._add_button.destroy()
            self._add_button = None

    def _update_add_button_state(self):
        """Disable the add button when the tab count reaches `max_tabs`."""
        if self._add_button is None:
            return
        at_limit = self._max_tabs is not None and len(self._tabs) >= self._max_tabs
        if at_limit:
            self._add_button.state(['disabled'])
        else:
            self._add_button.state(['!disabled'])

    def _on_add_click(self):
        """Handle add button click."""
        # Guard against a queued click that lands after the limit is reached.
        if self._max_tabs is not None and len(self._tabs) >= self._max_tabs:
            return
        self.event_generate('<<TabAdd>>')

    def on_tab_added(self, callback: Callable) -> str:
        """Register a callback for `<<TabAdd>>` events (fires when the add button is clicked).

        Args:
            callback: Called when the add button is clicked. `event.data` is None.

        Returns:
            Bind ID — pass to `off_tab_added()` to unsubscribe.
        """
        return self.bind('<<TabAdd>>', callback, add='+')

    def off_tab_added(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<TabAdd>>`.

        Args:
            bind_id: ID returned by `on_tab_added()`. If None, removes all.
        """
        self.unbind('<<TabAdd>>', bind_id)

    def on_tab_closed(self, callback: Callable) -> str:
        """Register a callback for `<<TabClose>>` events (fires when a tab's close button is clicked).

        Args:
            callback: Receives `event.data = {'value': Any}` — the closed tab's value.

        Returns:
            Bind ID — pass to `off_tab_closed()` to unsubscribe.
        """
        return self.bind('<<TabClose>>', callback, add='+')

    def off_tab_closed(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<TabClose>>`.

        Args:
            bind_id: ID returned by `on_tab_closed()`. If None, removes all.
        """
        self.unbind('<<TabClose>>', bind_id)

    def add(
        self,
        text: str = "",
        *,
        key: str = None,
        icon: str | dict = None,
        value: Any = None,
        closable: bool | Literal['hover'] | None = None,
        close_command: Callable = None,
        command: Callable = None,
        **kwargs
    ) -> TabItem:
        """Add a new tab to the tab bar.

        Args:
            text: Text to display on the tab.
            key: Unique identifier for the tab. Auto-generated if not provided.
            icon: Icon to display on the tab.
            value: Value associated with this tab for selection tracking.
                If None, defaults to the key.
            closable: Close button visibility (True, False, or 'hover').
                If None, uses the widget's `enable_closing` setting.
            close_command: Callback when close button is clicked.
            command: Callback when tab is selected.
            **kwargs: Additional arguments passed to TabItem.

        Returns:
            The created TabItem widget.

        Raises:
            ValueError: If a tab with the same key already exists.
        """
        # Auto-generate key if not provided
        if key is None:
            key = f"tab_{self._counter}"
            self._counter += 1

        if key in self._tabs:
            raise NavigationError(f"A tab with the key '{key}' already exists.")

        # Default value to key if not specified
        if value is None:
            value = key

        # Use widget-level default if not specified
        if closable is None:
            closable = self._enable_closing

        # Apply container defaults
        tab_kwargs = {
            'compound': self._compound,
            'orient': self._orient,
            'padding': self._tab_padding,
            'anchor': self._tab_anchor,
            'min_width': self._tab_min_width,
        }

        # Apply tab_width if specified (not 'stretch')
        if self._tab_width is not None and self._tab_width != 'stretch':
            tab_kwargs['width'] = self._tab_width

        # Apply accent if specified
        if self._accent is not None:
            tab_kwargs['accent'] = self._accent

        # Pass signal to TabItem for selection sync
        tab_kwargs['signal'] = self._signal

        # User kwargs override defaults
        tab_kwargs.update(kwargs)

        tab = TabItem(
            self._tab_bar,
            text=text,
            icon=icon,
            value=value,
            closable=closable,
            close_command=close_command,
            command=command,
            **tab_kwargs
        )

        # Determine pack options
        pack_opts = {'fill': 'x'}
        if self._tab_width == 'stretch' and self._orient == 'horizontal':
            pack_opts['expand'] = True

        if self._scrollable:
            # Tabs live inside the scroll region; the add/overflow buttons are
            # pinned outside it, so just append in order.
            tab.pack(**pack_opts)
            self._add_wheel_binding(tab)
            self._schedule_overflow_update()
        elif self._add_button is not None:
            tab.pack(before=self._add_button, **pack_opts)
        else:
            tab.pack(**pack_opts)

        # Track tab by key
        self._tabs[key] = tab
        self._tab_order.append(key)
        self._tab_values[key] = value
        self._tab_icons[key] = icon

        # Auto-select first tab
        if len(self._tabs) == 1:
            self._variable.set(value)

        self._update_add_button_state()
        return tab

    def remove(self, key: str) -> None:
        """Remove a tab by its key.

        Args:
            key: The key of the tab to remove.

        Raises:
            KeyError: If no tab with the given key exists.
        """
        if key not in self._tabs:
            raise NavigationError(f"No tab with key '{key}'")

        tab = self._tabs.pop(key)
        self._tab_order.remove(key)
        self._tab_values.pop(key, None)
        self._tab_icons.pop(key, None)
        tab.pack_forget()
        tab.destroy()
        self._update_add_button_state()
        self._schedule_overflow_update()

    def hide(self, key: str) -> None:
        """Hide a tab without removing it from the registry.

        The tab disappears from the bar but can be restored with `show()`.

        Args:
            key: Key of the tab to hide.

        Raises:
            KeyError: If no tab with the given key exists.
        """
        if key not in self._tabs:
            raise NavigationError(f"No tab with key '{key}'")
        if key not in self._hidden:
            self._hidden.add(key)
            self._tabs[key].pack_forget()
            self._schedule_overflow_update()

    def show(self, key: str) -> None:
        """Restore a previously hidden tab to the bar.

        Args:
            key: Key of the tab to show.

        Raises:
            KeyError: If no tab with the given key exists.
        """
        if key not in self._tabs:
            raise NavigationError(f"No tab with key '{key}'")
        if key in self._hidden:
            self._hidden.discard(key)
            tab = self._tabs[key]
            pack_opts: dict = {'fill': 'x'}
            if self._tab_width == 'stretch' and self._orient == 'horizontal':
                pack_opts['expand'] = True
            # Re-insert at the correct position relative to visible tabs
            next_visible = self._next_visible_tab_after(key)
            if next_visible is not None:
                tab.pack(before=self._tabs[next_visible], **pack_opts)
            elif self._add_button is not None and not self._scrollable:
                tab.pack(before=self._add_button, **pack_opts)
            else:
                tab.pack(**pack_opts)
            if self._scrollable:
                self._add_wheel_binding(tab)
                self._schedule_overflow_update()

    def _next_visible_tab_after(self, key: str) -> str | None:
        """Return the key of the next visible tab after *key* in tab order."""
        found = False
        for k in self._tab_order:
            if found and k not in self._hidden:
                return k
            if k == key:
                found = True
        return None

    # -------------------------------------------------------------------------
    # Overflow scrolling (scrollbar-less strip + trailing overflow menu)
    # -------------------------------------------------------------------------

    def _on_tabbar_configure(self, _event=None) -> None:
        """Keep the canvas cross-size matched to the strip; recheck overflow."""
        if not self._scrollable:
            return
        if self._axis == 'x':
            cross = self._tab_bar.winfo_reqheight()
        else:
            cross = self._tab_bar.winfo_reqwidth()
        if cross > 1 and cross != self._canvas_cross:
            self._canvas_cross = cross
            if self._axis == 'x':
                self._scroll.canvas.configure(height=cross)
            else:
                self._scroll.canvas.configure(width=cross)
        self._schedule_overflow_update()

    def _on_viewport_configure(self, _event=None) -> None:
        """Re-evaluate overflow when the visible viewport is resized."""
        self._schedule_overflow_update()

    def _content_size(self) -> int:
        """Total length of the tab strip along the scroll axis (pixels)."""
        if self._axis == 'x':
            return self._tab_bar.winfo_reqwidth()
        return self._tab_bar.winfo_reqheight()

    def _viewport_size(self) -> int:
        """Visible length of the scroll viewport along the scroll axis (pixels)."""
        canvas = self._scroll.canvas
        return canvas.winfo_width() if self._axis == 'x' else canvas.winfo_height()

    def _content_overflows(self) -> bool:
        """Whether the strip is longer than the viewport (tabs are off-screen)."""
        if not self._scrollable:
            return False
        view = self._viewport_size()
        return view > 1 and self._content_size() > view + 1

    def _view_first(self) -> float:
        """First-visible fraction (0..1) of the scroll axis."""
        view = self._scroll.xview() if self._axis == 'x' else self._scroll.yview()
        return view[0]

    def _view_moveto(self, fraction: float) -> None:
        """Scroll so *fraction* (0..1) of the content is at the leading edge."""
        if self._axis == 'x':
            self._scroll.xview_moveto(fraction)
        else:
            self._scroll.yview_moveto(fraction)

    def _tab_start(self, tab: TabItem) -> int:
        """Leading-edge offset of *tab* within the strip along the scroll axis."""
        return tab.winfo_x() if self._axis == 'x' else tab.winfo_y()

    def _tab_extent(self, tab: TabItem) -> int:
        """Length of *tab* along the scroll axis (pixels)."""
        return tab.winfo_width() if self._axis == 'x' else tab.winfo_height()

    def _schedule_overflow_update(self) -> None:
        """Coalesce overflow re-evaluation to the next idle moment."""
        if not self._scrollable or self._overflow_after is not None:
            return
        try:
            self._overflow_after = self.after_idle(self._update_overflow)
        except Exception:
            self._overflow_after = None

    def _update_overflow(self) -> None:
        """Show or hide the trailing overflow button to match overflow state."""
        self._overflow_after = None
        if not self._scrollable or not self.winfo_exists():
            return
        overflow = self._content_overflows()
        if overflow and not self._overflow_visible:
            self._show_overflow_button()
        elif not overflow and self._overflow_visible:
            self._hide_overflow_button()

    def _show_overflow_button(self) -> None:
        """Create (once) and pin the trailing overflow button.

        Horizontal uses a compact icon-only chevron; vertical uses a full-width,
        left-aligned `⌄ More` to match the tab rows and the `+ New` button.
        """
        if self._overflow_button is None:
            if self._axis == 'x':
                self._overflow_button = Button(
                    self._strip_row,
                    icon={'name': 'chevron-down', 'size': 16},
                    icon_only=True,
                    variant='ghost',
                    command=self._on_overflow_click,
                )
            else:
                self._overflow_button = Button(
                    self._strip_row,
                    text='More',
                    icon='chevron-down',
                    variant='ghost',
                    anchor='w',
                    command=self._on_overflow_click,
                )
        if self._axis == 'x':
            self._overflow_button.pack(side='right')
        else:
            self._overflow_button.pack(side='bottom', fill='x')
        self._overflow_visible = True

    def _hide_overflow_button(self) -> None:
        """Unpin the trailing overflow button (kept for reuse)."""
        if self._overflow_button is not None:
            self._overflow_button.pack_forget()
        self._overflow_visible = False

    def _offscreen_tab_keys(self) -> list[str]:
        """Keys of visible tabs that are not fully within the viewport."""
        if not self._scrollable:
            return []
        content = self._content_size()
        view = self._viewport_size()
        lead = self._view_first() * content
        trail = lead + view
        keys: list[str] = []
        for key in self._tab_order:
            if key in self._hidden:
                continue
            tab = self._tabs[key]
            start = self._tab_start(tab)
            end = start + self._tab_extent(tab)
            if start < lead - 1 or end > trail + 1:
                keys.append(key)
        return keys

    def _scroll_into_view(self, key: str, _retries: int = 3) -> None:
        """Scroll the strip so the tab for *key* is fully visible."""
        if not self._scrollable or key not in self._tabs or key in self._hidden:
            return
        if not self.winfo_exists():
            return
        tab = self._tabs[key]
        # A just-added tab may not be laid out yet (winfo_x/y still 0). Re-defer
        # rather than force a synchronous flush, which would paint a half-settled
        # layout and make the page visibly jump. Only the first tab legitimately
        # sits at offset 0.
        if _retries > 0 and key != self._tab_order[0] and self._tab_start(tab) == 0:
            self.after_idle(lambda: self._scroll_into_view(key, _retries - 1))
            return
        content = self._content_size()
        view = self._viewport_size()
        if view <= 1 or content <= view:
            return
        start = self._tab_start(tab)
        end = start + self._tab_extent(tab)
        lead = self._view_first() * content
        trail = lead + view
        if start < lead:
            new_lead = start
        elif end > trail:
            new_lead = end - view
        else:
            return
        new_lead = max(0, min(new_lead, content - view))
        self._view_moveto(new_lead / content)

    def _on_selection_scroll(self, value: Any) -> None:
        """Auto-scroll the newly selected tab into view (signal subscriber)."""
        if not self._scrollable:
            return
        key = self._key_for_value(value)
        if key is not None:
            self.after_idle(lambda: self._scroll_into_view(key))

    def _key_for_value(self, value: Any) -> str | None:
        """Reverse-map a selection value back to a tab key."""
        for key, val in self._tab_values.items():
            if val == value:
                return key
        return None

    def _ensure_overflow_menu(self):
        """Create (once) the dropdown used by the overflow button."""
        if self._overflow_menu is None:
            from bootstack.widgets._impl.composites.contextmenu import ContextMenu
            if self._axis == 'x':
                anchor, attach = 'ne', 'se'
            else:
                anchor, attach = 'sw', 'nw'
            self._overflow_menu = ContextMenu(
                self._overflow_button,
                target=self._overflow_button,
                trigger='manual',
                anchor=anchor,
                attach=attach,
                offset=(0, 2),
            )
        return self._overflow_menu

    def _on_overflow_click(self) -> None:
        """Populate and show the overflow dropdown with the off-screen tabs."""
        keys = self._offscreen_tab_keys()
        menu = self._ensure_overflow_menu()
        menu.items([])  # clear previous contents
        for key in keys:
            tab = self._tabs[key]
            try:
                label = tab.cget('text') or key
            except Exception:
                label = key
            icon = self._tab_icons.get(key)
            kw = {'text': label, 'command': lambda k=key: self._on_overflow_select(k)}
            if icon:
                kw['icon'] = icon
            menu.add_command(**kw)
        menu.show()

    def _on_overflow_select(self, key: str) -> None:
        """Select a tab chosen from the overflow menu and reveal it."""
        if key not in self._tab_values:
            return
        self._variable.set(self._tab_values[key])
        # Selection scroll also fires via the signal, but request it explicitly
        # too in case the value did not actually change.
        self.after_idle(lambda: self._scroll_into_view(key))

    def _setup_wheel_bindings(self) -> None:
        """Bind wheel scrolling along the strip axis via a private bindtag."""
        winsys = self.tk.call('tk', 'windowingsystem')
        if winsys == 'x11':
            self.bind_class(self._wheel_tag, '<Button-4>', self._on_strip_wheel, add='+')
            self.bind_class(self._wheel_tag, '<Button-5>', self._on_strip_wheel, add='+')
        else:
            self.bind_class(self._wheel_tag, '<MouseWheel>', self._on_strip_wheel, add='+')
        self._add_wheel_binding(self._tab_bar)

    def _add_wheel_binding(self, widget) -> None:
        """Add the wheel bindtag to *widget* and its descendants (idempotent)."""
        try:
            tags = list(widget.bindtags())
            if self._wheel_tag not in tags:
                tags.insert(1 if len(tags) > 1 else len(tags), self._wheel_tag)
                widget.bindtags(tuple(tags))
        except Exception:
            pass
        try:
            children = widget.winfo_children()
        except Exception:
            return
        for child in children:
            self._add_wheel_binding(child)

    def _on_strip_wheel(self, event) -> str | None:
        """Scroll the strip along its axis in response to the mouse wheel."""
        if not self._scrollable or not self._content_overflows():
            return None
        winsys = self.tk.call('tk', 'windowingsystem')
        if winsys == 'win32':
            notches = -event.delta / 120
        elif winsys == 'aqua':
            notches = -event.delta
        elif getattr(event, 'num', None) == 4:
            notches = -1
        elif getattr(event, 'num', None) == 5:
            notches = 1
        else:
            notches = 0
        if not notches:
            return 'break'
        content = self._content_size()
        view = self._viewport_size()
        if content <= view:
            return 'break'
        step = 60 * notches
        lead = self._view_first() * content
        lead = max(0, min(lead + step, content - view))
        self._view_moveto(lead / content)
        return 'break'

    def _on_overflow_destroy(self, event) -> None:
        """Release overflow resources when the tab strip is destroyed."""
        if event.widget is not self:
            return
        if self._overflow_after is not None:
            try:
                self.after_cancel(self._overflow_after)
            except Exception:
                pass
            self._overflow_after = None
        if self._overflow_menu is not None:
            try:
                self._overflow_menu.destroy()
            except Exception:
                pass
            self._overflow_menu = None

    def item(self, key: str) -> TabItem:
        """Get a tab by its key.

        Args:
            key: The key of the tab to retrieve.

        Returns:
            The TabItem instance.

        Raises:
            KeyError: If no tab with the given key exists.
        """
        if key not in self._tabs:
            raise NavigationError(f"No tab with key '{key}'")
        return self._tabs[key]

    def items(self) -> tuple[TabItem, ...]:
        """Get all tab widgets in order.

        Returns:
            A tuple of all TabItem instances in the order they were added.
        """
        return tuple(self._tabs[key] for key in self._tab_order)

    def keys(self) -> tuple[str, ...]:
        """Get all tab keys in order.

        Returns:
            A tuple of all tab keys in the order they were added.
        """
        return tuple(self._tab_order)

    def configure_item(self, key: str, option: str = None, **kwargs: Any):
        """Configure a specific tab by its key.

        Args:
            key: The key of the tab to configure.
            option: If provided, return the value of this option.
            **kwargs: Configuration options to apply to the tab.

        Returns:
            If option is provided, returns the value of that option.
        """
        tab = self.item(key)
        if option is not None:
            return tab.cget(option)
        tab.configure(**kwargs)

    @configure_delegate('orient')
    def _delegate_orient(self, value=None):
        """Get orientation (read-only after creation)."""
        if value is None:
            return self._orient
        raise ValueError("orient cannot be changed after creation")

    @configure_delegate('variant')
    def _delegate_variant(self, value=None):
        """Get variant (read-only after creation)."""
        if value is None:
            return self._variant
        raise ValueError("variant cannot be changed after creation")

    @property
    def variable(self) -> tk.Variable:
        """Get the underlying tk.Variable for tab selection.

        See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
        """
        return self._variable

    @property
    def signal(self) -> 'Signal[Any]':
        """Get the Signal for tab selection."""
        return self._signal

    @configure_delegate('show_divider')
    def _delegate_show_divider(self, value=None):
        """Get or set whether the divider is shown."""
        if value is None:
            return self._show_divider
        if value != self._show_divider:
            self._show_divider = value
            if value:
                self._create_divider()
            else:
                self._destroy_divider()

    def get(self) -> str:
        """Return the currently selected tab value."""
        return self._variable.get()

    def set(self, value: str) -> None:
        """Set the selected tab value."""
        self._variable.set(value)

    @property
    def value(self) -> str:
        """Get or set the selected tab value."""
        return self.get()

    @value.setter
    def value(self, value: str) -> None:
        self.set(value)

    @configure_delegate('value')
    def _delegate_value(self, value=None):
        """Get or set the value via configure."""
        if value is None:
            return self.get()
        self.set(value)

    def on_tab_changed(self, callback: Callable) -> Any:
        """Register a callback for tab selection changes.

        Args:
            callback: Called with the new selected tab value (str) when the
                selection changes.

        Returns:
            Subscription ID — pass to `off_tab_changed()` to unsubscribe.
        """
        return self._signal.subscribe(callback)

    def off_tab_changed(self, bind_id: Any) -> None:
        """Cancel a subscription created by `on_tab_changed()`.

        Args:
            bind_id: The handle returned by `on_tab_changed()`.
        """
        if bind_id is not None:
            bind_id.cancel()
