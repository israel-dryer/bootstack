"""Scrolled text widget with configurable scrollbars."""
import tkinter
from typing import Any, Literal

from bootstack.widgets._impl.primitives.frame import Frame
from bootstack.widgets._impl.mixins.configure_mixin import configure_delegate
from bootstack.widgets._impl.primitives.scrollbar import Scrollbar
from bootstack.widgets.types import Master

ScrollDirection = Literal['horizontal', 'vertical', 'both']
ScrollbarVisibility = Literal['always', 'never', 'hover', 'scroll']


class ScrolledText(Frame):
    """A text widget with configurable scrollbars and mouse wheel support.

    The ScrolledText widget provides a Text widget with scrollbars that can be
    configured to appear always, never, on hover, or when scrolling. Full mouse
    wheel support is included.

    This widget delegates all Text methods to the internal text widget, so it
    can be used just like a standard Text widget with additional scrolling
    functionality.
    """

    def __init__(
            self,
            master: Master = None,
            padding: int = 0,
            scroll_direction: ScrollDirection = 'vertical',
            scrollbar_visibility: ScrollbarVisibility = 'always',
            autohide_delay: int = 1000,
            scrollbar_style: str = 'default',
            **kwargs: Any,
    ):
        """
        Args:
            master: The parent widget.
            padding: Padding around the frame container.
            scroll_direction: Scroll direction — `'vertical'`, `'horizontal'`, or `'both'`.
                Use `'both'` to enable horizontal scrolling with Shift+MouseWheel.
            scrollbar_visibility: When scrollbars are shown — `'always'`, `'never'`,
                `'hover'` (on mouse enter), or `'scroll'` (auto-hide after delay).
            autohide_delay: Milliseconds before scrollbars hide in `'scroll'` mode.
                Default is 1000.
            scrollbar_style: Accent token for the scrollbars (e.g., `'primary'`).
            **kwargs: Additional keyword arguments passed to the `Text` widget.
        """
        # Initialize Frame
        super().__init__(master=master, padding=padding)

        # Configuration
        self._direction = scroll_direction
        self._scrollbar_visibility = scrollbar_visibility
        self._autohide_delay = autohide_delay
        self._scrollbar_style = scrollbar_style
        self._hide_timer = None

        # Create unique bind tag for this scrolledtext
        self._scroll_tag = f'ScrolledText_{id(self)}'

        # Detect windowing system
        self.winsys = self.tk.call("tk", "windowingsystem")

        # Bind scroll events to our custom tag
        self._setup_scroll_tag_bindings()

        # Create text widget
        text_kwargs = kwargs.copy()

        # Set wrap mode based on direction
        if scroll_direction == 'both' or scroll_direction == 'horizontal':
            if 'wrap' not in text_kwargs:
                text_kwargs['wrap'] = 'none'

        self._text = tkinter.Text(self, **text_kwargs)

        # Create scrollbars
        self._vertical_scrollbar = Scrollbar(
            master=self,
            orient='vertical',
            command=self._text.yview,
            accent=scrollbar_style if scrollbar_style != 'default' else None
        )
        self._horizontal_scrollbar = Scrollbar(
            master=self,
            orient='horizontal',
            command=self._text.xview,
            accent=scrollbar_style if scrollbar_style != 'default' else None
        )

        # Configure text scrolling
        if scroll_direction in ('vertical', 'both'):
            self._text.configure(yscrollcommand=self._on_text_scroll_y)
        if scroll_direction in ('horizontal', 'both'):
            self._text.configure(xscrollcommand=self._on_text_scroll_x)

        # Layout
        self._layout_widgets()

        # Bind events for autohide/hover
        self._bind_container_events()

        # Initial scrollbar visibility
        self._update_scrollbar_visibility()

        # Add scroll bindings to text widget
        self._add_scroll_binding(self._text)

        # Delegate text methods to this widget (except geometry managers)
        for method in vars(tkinter.Text).keys():
            if any(["pack" in method, "grid" in method, "place" in method]):
                pass
            else:
                # Don't override methods that already exist
                if not hasattr(self, method):
                    setattr(self, method, getattr(self._text, method))

    @configure_delegate('scroll_direction')
    def _delegate_scroll_direction(self, value=None):
        """Get or set the scroll direction ('vertical', 'horizontal', or 'both')."""
        if value is None:
            return self._direction
        else:
            self._direction = value
            # Update scrollbar visibility and layout
            self._update_scrollbar_visibility()
        return None

    @configure_delegate('scrollbar_visibility')
    def _delegate_scrollbar_visibility(self, value=None):
        """Get or set the scrollbar visibility mode ('always', 'never', 'hover', 'scroll')."""
        if value is None:
            return self._scrollbar_visibility
        else:
            old_value = self._scrollbar_visibility
            self._scrollbar_visibility = value

            # Unbind old events if changing from hover
            if old_value == 'hover':
                self.unbind('<Enter>')
                self.unbind('<Leave>')
                self._text.unbind('<Enter>')
                self._text.unbind('<Leave>')
                self._vertical_scrollbar.unbind('<Enter>')
                self._vertical_scrollbar.unbind('<Leave>')
                self._horizontal_scrollbar.unbind('<Enter>')
                self._horizontal_scrollbar.unbind('<Leave>')

            # Bind new events and update scrollbar visibility
            self._bind_container_events()
            self._update_scrollbar_visibility()
        return None

    @configure_delegate('autohide_delay')
    def _delegate_autohide_delay(self, value=None):
        """Get or set the milliseconds before scrollbars hide in 'scroll' mode."""
        if value is None:
            return self._autohide_delay
        else:
            self._autohide_delay = value
        return None

    @configure_delegate('scrollbar_style')
    def _delegate_scrollbar_style(self, value=None):
        """Get or set the accent token applied to both scrollbars."""
        if value is None:
            return self._scrollbar_style
        else:
            self._scrollbar_style = value
            # Apply the new accent to both scrollbars
            if value and value != 'default':
                self._vertical_scrollbar.configure(accent=value)
                self._horizontal_scrollbar.configure(accent=value)
        return None

    def _setup_scroll_tag_bindings(self):
        """Setup bindings on our custom bind tag."""
        if self.winsys.lower() == "x11":
            self.bind_class(self._scroll_tag, "<Button-4>", self._on_mousewheel)
            self.bind_class(self._scroll_tag, "<Button-5>", self._on_mousewheel)
            self.bind_class(self._scroll_tag, "<Shift-Button-4>", self._on_shift_mousewheel)
            self.bind_class(self._scroll_tag, "<Shift-Button-5>", self._on_shift_mousewheel)
        else:
            self.bind_class(self._scroll_tag, "<MouseWheel>", self._on_mousewheel)
            self.bind_class(self._scroll_tag, "<Shift-MouseWheel>", self._on_shift_mousewheel)

    def _layout_widgets(self):
        """Layout the text widget and scrollbars."""
        self._text.grid(row=0, column=0, sticky='nsew')

        if self._direction in ('vertical', 'both'):
            self._vertical_scrollbar.grid(row=0, column=1, sticky='ns')

        if self._direction in ('horizontal', 'both'):
            self._horizontal_scrollbar.grid(row=1, column=0, sticky='ew')

        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Initially hide scrollbars based on scrollbar_visibility setting
        if self._scrollbar_visibility == 'never':
            self._vertical_scrollbar.grid_remove()
            self._horizontal_scrollbar.grid_remove()
        elif self._scrollbar_visibility in ('hover', 'scroll'):
            self._vertical_scrollbar.grid_remove()
            self._horizontal_scrollbar.grid_remove()

    def _bind_container_events(self):
        """Bind events for the container (enter/leave for autohide)."""
        if self._scrollbar_visibility == 'hover':
            self.bind('<Enter>', self._on_container_enter)
            self.bind('<Leave>', self._on_container_leave)
            self._text.bind('<Enter>', self._on_container_enter)
            self._text.bind('<Leave>', self._on_container_leave)
            self._vertical_scrollbar.bind('<Enter>', self._on_container_enter)
            self._vertical_scrollbar.bind('<Leave>', self._on_container_leave)
            self._horizontal_scrollbar.bind('<Enter>', self._on_container_enter)
            self._horizontal_scrollbar.bind('<Leave>', self._on_container_leave)

    def _on_container_enter(self, event):
        """Handle mouse entering the container."""
        if self._scrollbar_visibility == 'hover':
            self._show_scrollbars()

    def _on_container_leave(self, event):
        """Handle mouse leaving the container."""
        if self._scrollbar_visibility == 'hover':
            self._hide_scrollbars()

    def _show_scrollbars(self):
        """Show scrollbars."""
        if self._direction in ('vertical', 'both'):
            self._vertical_scrollbar.grid()
        if self._direction in ('horizontal', 'both'):
            self._horizontal_scrollbar.grid()

    def _hide_scrollbars(self):
        """Hide scrollbars."""
        self._vertical_scrollbar.grid_remove()
        self._horizontal_scrollbar.grid_remove()

    def _on_text_scroll_y(self, first, last):
        """Update vertical scrollbar position."""
        self._vertical_scrollbar.set(first, last)

    def _on_text_scroll_x(self, first, last):
        """Update horizontal scrollbar position."""
        self._horizontal_scrollbar.set(first, last)

    def _update_scrollbar_visibility(self):
        """Update scrollbar visibility based on current mode."""
        if self._scrollbar_visibility == 'always':
            self._show_scrollbars()
        elif self._scrollbar_visibility == 'never':
            self._hide_scrollbars()

    def _on_mousewheel(self, event):
        """Handle vertical mouse wheel scrolling."""
        # Show scrollbar temporarily in scroll mode
        if self._scrollbar_visibility == 'scroll':
            self._show_scrollbars()
            if self._hide_timer:
                self.after_cancel(self._hide_timer)
            self._hide_timer = self.after(self._autohide_delay, self._hide_scrollbars)

        # Calculate delta based on platform
        delta = 0
        if self.winsys.lower() == "win32":
            delta = -int(event.delta / 120)
        elif self.winsys.lower() == "aqua":
            delta = -event.delta
        elif event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1

        # Scroll vertically
        if self._direction in ('vertical', 'both') and delta != 0:
            self._text.yview_scroll(delta, 'units')

    def _on_shift_mousewheel(self, event):
        """Handle horizontal mouse wheel scrolling (Shift+MouseWheel)."""
        # Show scrollbar temporarily in scroll mode
        if self._scrollbar_visibility == 'scroll':
            self._show_scrollbars()
            if self._hide_timer:
                self.after_cancel(self._hide_timer)
            self._hide_timer = self.after(self._autohide_delay, self._hide_scrollbars)

        # Calculate delta based on platform
        delta = 0
        if self.winsys.lower() == "win32":
            delta = -int(event.delta / 120)
        elif self.winsys.lower() == "aqua":
            delta = -event.delta
        elif event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1

        # Scroll horizontally
        if self._direction in ('horizontal', 'both') and delta != 0:
            self._text.xview_scroll(delta, 'units')

    def _add_scroll_binding(self, widget):
        """Add scroll bind tag to widget."""
        try:
            tags = list(widget.bindtags())
            if self._scroll_tag not in tags:
                if len(tags) >= 2:
                    tags.insert(1, self._scroll_tag)
                else:
                    tags.append(self._scroll_tag)
                widget.bindtags(tuple(tags))
        except:
            pass

    def destroy(self):
        """Clean up resources and destroy the widget."""
        # Cancel any pending timer
        if self._hide_timer:
            self.after_cancel(self._hide_timer)
            self._hide_timer = None

        # Unbind class bindings for the scroll tag
        if self.winsys.lower() == "x11":
            self.unbind_class(self._scroll_tag, "<Button-4>")
            self.unbind_class(self._scroll_tag, "<Button-5>")
            self.unbind_class(self._scroll_tag, "<Shift-Button-4>")
            self.unbind_class(self._scroll_tag, "<Shift-Button-5>")
        else:
            self.unbind_class(self._scroll_tag, "<MouseWheel>")
            self.unbind_class(self._scroll_tag, "<Shift-MouseWheel>")

        # Call parent destroy
        super().destroy()

    def __getattr__(self, name: str) -> Any:
        """Delegate unknown attribute access to the internal Text widget.

        Args:
            name: The attribute name to access.

        Returns:
            The attribute from the internal Text widget.

        Raises:
            AttributeError: If _text doesn't exist yet or doesn't have the attribute.
        """
        # Avoid infinite recursion during initialization
        if '_text' not in self.__dict__:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        return getattr(self._text, name)

    @property
    def vertical_scrollbar(self) -> Scrollbar:
        """The vertical scrollbar widget."""
        return self._vertical_scrollbar

    @property
    def horizontal_scrollbar(self) -> Scrollbar:
        """The horizontal scrollbar widget."""
        return self._horizontal_scrollbar

    @property
    def text(self):
        """Get the internal text widget.

        Returns:
            The underlying Text widget instance.
        """
        return self._text

