"""Toolbar widget with customizable content and optional window controls."""

from __future__ import annotations

import sys
from tkinter import Widget
from typing import TYPE_CHECKING, Any, Callable, Literal

from typing_extensions import TypedDict, Unpack

from bootstack.widgets._impl.primitives.frame import Frame
from bootstack.widgets._impl.primitives.button import Button
from bootstack.widgets._impl.primitives.label import Label
from bootstack.widgets._impl.primitives.separator import Separator
from bootstack.widgets._impl.mixins import configure_delegate
from bootstack.widgets.types import Master, SurfaceToken, WidgetDensity

if TYPE_CHECKING:
    from tkinter import StringVar

    from bootstack.widgets._impl.composites.dropdownbutton import DropdownButton
    from bootstack.widgets._impl.composites.menu.model import MenuGroup, MenuModel


class ToolbarKwargs(TypedDict, total=False):
    show_window_controls: bool
    draggable: bool
    button_variant: str
    density: WidgetDensity
    padding: Any
    # Frame options
    width: int
    height: int
    surface: SurfaceToken | str
    show_border: bool


class Toolbar(Frame):
    """A horizontal toolbar with customizable content and optional window controls.

    Toolbar provides a container for icon buttons, labels, and other widgets
    arranged horizontally. It optionally supports window control buttons
    (minimize, maximize, close) and window dragging for custom titlebars.

    Items are added from left to right. Use `add_spacer()` to push
    subsequent items to the right side.

    """

    def __init__(
        self,
        master: Master = None,
        show_window_controls: bool = False,
        draggable: bool = False,
        button_variant: str = 'ghost',
        density: Literal['default', 'compact'] = 'default',
        padding: int | tuple = None,
        **kwargs: Unpack[ToolbarKwargs]
    ):
        """Initialize a Toolbar.

        Args:
            master: Parent widget.
            show_window_controls: Show minimize/maximize/close buttons. Default False.
            draggable: Enable window dragging by clicking and dragging the toolbar.
                Default False.
            button_variant: Default variant for toolbar buttons. Default 'ghost'.
            density: Button density for toolbar items. 'compact' for smaller buttons,
                'default' for standard size. Default 'default'.
            padding: Toolbar padding. If None, uses a uniform density-based
                default (2 for compact, 3 for default) so items have even
                breathing room on all sides.
            **kwargs: Additional arguments passed to Frame.
        """
        if padding is None:
            padding = 2 if density == 'compact' else 3
        super().__init__(master, padding=padding, **kwargs)

        self._show_window_controls = show_window_controls
        self._draggable = draggable or show_window_controls  # Auto-enable drag with window controls
        self._button_variant = button_variant
        self._density = density

        # Content container (left side)
        self._content_frame = Frame(self)
        self._content_frame.pack(side='left', fill='both', expand=True)

        # Window controls container (right side)
        self._controls_frame: Frame | None = None
        if show_window_controls:
            self._build_window_controls()

        # Drag state
        self._drag_start_x = 0
        self._drag_start_y = 0

        if self._draggable:
            self._setup_drag()

        # Menu state — populated lazily by add_menu(). The model is the single
        # source of truth for this toolbar's menus (so a host can aggregate them
        # for the macOS native bar); the triggers are the in-window dropdowns.
        self._menu_model: MenuModel | None = None
        self._menu_triggers: dict[str, DropdownButton] = {}
        self._menu_radio_vars: dict[str, StringVar] = {}
        self._menu_rebind_pending: Any = None
        # Optional host hook fired when this toolbar's menus change, so a window
        # can rebuild the aggregated macOS native menu bar.
        self._on_menu_change: Callable[[], Any] | None = None

        # Cancel a pending menu-shortcut rebind if the bar is destroyed first.
        self.bind("<Destroy>", self._on_destroy, add="+")

    @staticmethod
    def _control_glyph(name: str) -> dict:
        """A title-bar control glyph spec — a small (~14px) glyph regardless of
        the toolbar density, for a tight native-style control rather than a
        chunky compact-icon button (the 17px compact-icon default)."""
        return {'name': name, 'size': 14}

    def _build_window_controls(self):
        """Build window control buttons (minimize, maximize, close)."""
        self._controls_frame = Frame(self)
        self._controls_frame.pack(side='right', fill='y', padx=(8, 0))

        # Minimize button
        self._minimize_btn = Button(
            self._controls_frame,
            icon=self._control_glyph('dash-lg'),
            icon_only=True,
            variant='ghost',
            density='compact',
            surface=self._surface,
            command=self._on_minimize,
        )
        self._minimize_btn.pack(side='left', padx=2)

        # Maximize/Restore button
        self._maximize_btn = Button(
            self._controls_frame,
            icon=self._control_glyph('fullscreen'),
            icon_only=True,
            variant='ghost',
            density='compact',
            surface=self._surface,
            command=self._on_maximize,
        )
        self._maximize_btn.pack(side='left', padx=2)

        # Close button — danger accent so it hovers red (the native convention).
        self._close_btn = Button(
            self._controls_frame,
            icon=self._control_glyph('x-lg'),
            icon_only=True,
            variant='ghost',
            accent='danger',
            density='compact',
            surface=self._surface,
            command=self._on_close,
        )
        self._close_btn.pack(side='left', padx=2)

        # Disable maximize if window is not resizable (checked after idle so
        # the window geometry is finalised).
        self.after_idle(self._sync_maximize_state)

    def _sync_maximize_state(self) -> None:
        """Hide the maximize button when the window is not resizable."""
        try:
            w, h = self.winfo_toplevel().resizable()
            if not w and not h:
                self._maximize_btn.pack_forget()
        except Exception:
            pass

    def _on_minimize(self):
        """Minimize the window, keeping it recoverable from the taskbar."""
        window = self.winfo_toplevel()
        if not window.overrideredirect():
            window.iconify()
            return
        # A borderless (override_redirect) window has no taskbar button by
        # default, so a plain iconify() would leave it with no way back. On
        # Windows, give it the APPWINDOW taskbar style and minimize via the Win32
        # API — it stays borderless and the taskbar button restores it. Elsewhere,
        # fall back to briefly restoring native decorations (which grant a taskbar
        # button), iconify, then re-hide them once the user restores it.
        if sys.platform == 'win32' and self._win32_minimize(window):
            return
        window.update_idletasks()
        window.overrideredirect(False)
        window.update_idletasks()
        window.iconify()
        window.bind('<Map>', self._on_restore_override_redirect, add='+')

    def _win32_minimize(self, window) -> bool:
        """Minimize a borderless window via Win32, with a taskbar button.

        Adds `WS_EX_APPWINDOW` (and drops `WS_EX_TOOLWINDOW`) so the borderless
        window gets a taskbar button, then minimizes it. Returns True on success.
        """
        try:
            from ctypes import windll

            GWL_EXSTYLE = -20
            WS_EX_APPWINDOW = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080
            SW_HIDE, SW_SHOW, SW_MINIMIZE = 0, 5, 6

            hwnd = windll.user32.GetParent(window.winfo_id()) or window.winfo_id()
            style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            new_style = (style & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW
            if new_style != style:
                windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
                # The taskbar only re-reads the style on a re-show, so cycle the
                # window once (a brief flash) the first time the style changes.
                windll.user32.ShowWindow(hwnd, SW_HIDE)
                windll.user32.ShowWindow(hwnd, SW_SHOW)
            windll.user32.ShowWindow(hwnd, SW_MINIMIZE)
            return True
        except Exception:
            return False

    def _on_restore_override_redirect(self, event=None) -> None:
        """Restore override_redirect after the window is deiconified."""
        window = self.winfo_toplevel()
        if event is not None and getattr(event, 'widget', window) is not window:
            return
        window.unbind('<Map>')
        window.overrideredirect(True)

    def _on_maximize(self):
        """Handle maximize/restore button click."""
        window = self.winfo_toplevel()
        w, h = window.resizable()
        if not w and not h:
            return
        if window.state() == 'zoomed':
            window.state('normal')
            self._maximize_btn.configure(icon=self._control_glyph('fullscreen'))
        else:
            window.state('zoomed')
            self._maximize_btn.configure(icon=self._control_glyph('fullscreen-exit'))

    def _on_close(self):
        """Handle close button click."""
        window = self.winfo_toplevel()
        window.destroy()

    def _setup_drag(self):
        """Set up window dragging (and double-click-to-maximize) bindings."""
        for widget in (self, self._content_frame):
            widget.bind('<Button-1>', self._on_drag_start, add='+')
            widget.bind('<B1-Motion>', self._on_drag_motion, add='+')
            widget.bind('<Double-Button-1>', self._on_drag_double, add='+')

    def _on_drag_start(self, event):
        """Record drag start position."""
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root

    def _on_drag_motion(self, event):
        """Handle drag motion to move window."""
        window = self.winfo_toplevel()

        # A maximized window snaps back to its normal size before it can move.
        # The grab offset was captured against the *maximized* width, so simply
        # restoring would leave the window offset from the cursor (#165). Keep the
        # pointer on the title bar: capture where the cursor sits over the
        # maximized window (its horizontal fraction + vertical offset), restore,
        # then reposition the smaller window so the cursor lands at the same spot.
        if window.state() == 'zoomed':
            max_w = max(window.winfo_width(), 1)
            frac_x = (event.x_root - window.winfo_rootx()) / max_w
            offset_y = event.y_root - window.winfo_rooty()
            try:
                window.state('normal')
            except Exception:
                pass
            window.update_idletasks()
            new_x = int(event.x_root - frac_x * window.winfo_width())
            new_y = int(event.y_root - offset_y)
            window.geometry(f'+{new_x}+{new_y}')
            self._sync_maximize_icon('fullscreen')
            self._drag_start_x = event.x_root
            self._drag_start_y = event.y_root
            return

        # Calculate delta
        dx = event.x_root - self._drag_start_x
        dy = event.y_root - self._drag_start_y

        # Get current position
        x = window.winfo_x() + dx
        y = window.winfo_y() + dy

        # Move window
        window.geometry(f'+{x}+{y}')

        # Update drag start for next motion
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root

    def _on_drag_double(self, _event):
        """Double-clicking the bar toggles the window's maximized state."""
        self._on_maximize()
        return 'break'

    def _sync_maximize_icon(self, name: str) -> None:
        """Keep the maximize button's icon in sync with the window state."""
        btn = getattr(self, '_maximize_btn', None)
        if btn is not None:
            try:
                btn.configure(icon=self._control_glyph(name))
            except Exception:
                pass

    # --- Public API: Adding Items ---

    def add_button(
        self,
        icon: str | dict = None,
        text: str = None,
        command: Callable = None,
        accent: str = None,
        variant: str = None,
        **kwargs
    ) -> Button:
        """Add a button to the toolbar.

        Args:
            icon: Icon name or configuration.
            text: Button text. If None and icon provided, creates icon-only button.
            command: Button click callback.
            accent: Button accent token.
            variant: Button variant. Uses toolbar default if None.
            **kwargs: Additional arguments passed to Button.

        Returns:
            Button: The created button.
        """
        btn = Button(
            self._content_frame,
            icon=icon,
            text=text,
            icon_only=(icon is not None and text is None),
            command=command,
            accent=accent,
            variant=variant or self._button_variant,
            density=kwargs.pop('density', self._density),
            surface=kwargs.pop('surface', self._surface),
            **kwargs
        )
        btn.pack(side='left')
        return btn

    def add_menu(self, text: str, *, key: str | None = None) -> "MenuGroup":
        """Add a dropdown menu (File / Edit / …) as a toolbar item.

        Returns the menu's `MenuGroup` builder — add items with
        `add_action` / `add_check` / `add_radio` / `add_divider`, ideally in a
        `with` block. On Windows/Linux the menu renders as an in-window dropdown
        trigger in the toolbar; the menu also feeds this toolbar's menu model so a
        host can surface it in the macOS native menu bar.

        Args:
            text: The menu's label (e.g. `'File'`).
            key: Optional stable identifier; defaults to `text`.

        Returns:
            The `MenuGroup` for this menu.
        """
        from bootstack.widgets._impl.composites.dropdownbutton import DropdownButton
        from bootstack.widgets._impl.composites.menu.model import MenuModel

        if self._menu_model is None:
            self._menu_model = MenuModel()
        group = self._menu_model.add_menu(text, key=key)

        # A flat menu-bar-style trigger whose popdown is the themed context menu.
        trigger = DropdownButton(
            self._content_frame,
            text=text,
            items=[],
            variant='menubar-item',
            show_dropdown_button=False,
            density=self._density,
            surface=self._surface,
        )
        trigger.pack(side='left')
        self._menu_triggers[group.key] = trigger

        # Items are appended to the trigger as they are added to the group (the
        # build-up case), so the `with tb.add_menu(...)` block renders live; each
        # change also (coalesced) rebinds the model's keyboard shortcuts.
        group.on_change = lambda g=group, t=trigger: self._on_menu_item_added(g, t)
        return group

    def _on_menu_item_added(self, group: "MenuGroup", trigger: "DropdownButton") -> None:
        from bootstack.widgets._impl.composites.menu.render_themed import (
            menu_item_to_context_item,
        )

        item = group.items[-1]
        trigger.add_items([menu_item_to_context_item(item, self._menu_radio_vars)])
        self._schedule_menu_rebind()
        if self._on_menu_change is not None:
            self._on_menu_change()

    def _schedule_menu_rebind(self) -> None:
        """Coalesce shortcut (re)binding to idle so a built menu binds once."""
        if self._menu_rebind_pending is not None:
            try:
                self.after_cancel(self._menu_rebind_pending)
            except Exception:
                pass
        try:
            self._menu_rebind_pending = self.after_idle(self._rebind_menu_shortcuts)
        except Exception:
            self._rebind_menu_shortcuts()

    def _rebind_menu_shortcuts(self) -> None:
        self._menu_rebind_pending = None
        if self._menu_model is not None:
            try:
                self._menu_model.bind_shortcuts(self.winfo_toplevel())
            except Exception:
                pass

    def _on_destroy(self, event: Any) -> None:
        """Cancel a pending menu-shortcut rebind when the toolbar is destroyed.

        `<Destroy>` propagates up from descendants, so act only for the bar itself.
        """
        if event.widget is not self:
            return
        if self._menu_rebind_pending is not None:
            try:
                self.after_cancel(self._menu_rebind_pending)
            except Exception:
                pass
            self._menu_rebind_pending = None

    @property
    def menu_model(self) -> "MenuModel | None":
        """This toolbar's menu model (or `None` if no menus were added)."""
        return self._menu_model

    def add_label(
        self,
        text: str = '',
        icon: str | dict = None,
        font: str = None,
        **kwargs
    ) -> Label:
        """Add a label to the toolbar.

        Args:
            text: Label text.
            icon: Optional icon name or configuration.
            font: Font specification.
            **kwargs: Additional arguments passed to Label.

        Returns:
            Label: The created label.
        """
        # Show icon AND text when both are given. The internal Label primitive
        # defaults to icon-only (no compound) — the public Label wrapper's
        # compound logic doesn't run on this path, so set it here.
        has_text = bool(text) or kwargs.get('textsignal') is not None
        if icon is not None and has_text and 'compound' not in kwargs:
            kwargs['compound'] = 'left'
        lbl = Label(
            self._content_frame,
            text=text,
            icon=icon,
            font=font,
            surface=kwargs.pop('surface', self._surface),
            **kwargs
        )
        lbl.pack(side='left', padx=4)
        self._attach_drag(lbl)
        return lbl

    def _attach_drag(self, widget) -> None:
        """Wire window-drag bindings onto a child widget so the bar can be
        grabbed there (used for a draggable titlebar). No-op when the bar is not
        draggable. Buttons are intentionally excluded — they are click targets."""
        if not self._draggable:
            return
        widget.bind('<Button-1>', self._on_drag_start, add='+')
        widget.bind('<B1-Motion>', self._on_drag_motion, add='+')
        widget.bind('<Double-Button-1>', self._on_drag_double, add='+')

    def add_separator(self, length: int = 16, **kwargs) -> Separator:
        """Add a vertical separator to the toolbar.

        Args:
            length: Fixed length in pixels. If None, stretches to fill the
                toolbar height.
            **kwargs: Additional arguments passed to Separator.

        Returns:
            Separator: The created separator.
        """
        sep = Separator(
            self._content_frame,
            orient='vertical',
            length=length,
            **kwargs
        )
        # Only fill='y' if no fixed length specified
        if length:
            sep.pack(side='left', padx=4)
        else:
            sep.pack(side='left', fill='y', padx=4)
        return sep

    def add_spacer(self) -> Frame:
        """Add a flexible spacer that pushes subsequent items to the right.

        Returns:
            Frame: The spacer frame.
        """
        spacer = Frame(self._content_frame)
        spacer.pack(side='left', fill='both', expand=True)
        self._attach_drag(spacer)
        return spacer

    def add_widget(self, widget: Widget, **pack_kwargs) -> Widget:
        """Add a custom widget to the toolbar.

        The widget must already be created with the toolbar's content frame
        as its parent. Use `toolbar.content` to get the parent frame.

        Args:
            widget: The widget to add.
            **pack_kwargs: Arguments passed to pack(). Defaults to side='left'.

        Returns:
            Widget: The added widget.
        """
        pack_kwargs.setdefault('side', 'left')
        pack_kwargs.setdefault('padx', 2)
        widget.pack(**pack_kwargs)
        return widget

    # --- Properties ---

    @property
    def content(self) -> Frame:
        """Get the content frame for adding custom widgets."""
        return self._content_frame

    @property
    def show_window_controls(self) -> bool:
        """Check if window controls are shown."""
        return self._show_window_controls

    @property
    def draggable(self) -> bool:
        """Check if toolbar is draggable."""
        return self._draggable

    @property
    def density(self) -> str:
        """Get the toolbar's button density."""
        return self._density

    @property
    def surface(self) -> str:
        """The surface token applied to this toolbar."""
        return getattr(self, "_surface", "chrome")

    # --- Window Control Access ---

    @property
    def minimize_button(self) -> Button | None:
        """Get the minimize button (if window controls are shown)."""
        return getattr(self, '_minimize_btn', None)

    @property
    def maximize_button(self) -> Button | None:
        """Get the maximize button (if window controls are shown)."""
        return getattr(self, '_maximize_btn', None)

    @property
    def close_button(self) -> Button | None:
        """Get the close button (if window controls are shown)."""
        return getattr(self, '_close_btn', None)

    # --- Configuration Delegates ---

    @configure_delegate('density')
    def _delegate_density(self, value: str = None):
        """Configure the toolbar's default button density."""
        if value is None:
            return self._density
        self._density = value
        return None

    @configure_delegate('button_variant')
    def _delegate_button_variant(self, value: str = None):
        """Configure the toolbar's default button variant."""
        if value is None:
            return self._button_variant
        self._button_variant = value
        return None