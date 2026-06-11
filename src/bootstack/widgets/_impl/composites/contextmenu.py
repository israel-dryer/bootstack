"""Context menu widget for displaying popup menus.

Provides a customizable context menu with support for commands, checkbuttons,
radiobuttons, and separators.
"""

from tkinter import BooleanVar, IntVar, Misc, StringVar, TclError, Toplevel, Widget
from typing_extensions import Unpack
from typing import Any, Callable, Literal

from bootstack._runtime.window_utilities import AnchorPoint
from bootstack.widgets.types import WidgetDensity

from bootstack._runtime.shortcuts import get_shortcuts, format_shortcut
from bootstack.style.bootstyle_builder_base import BootstyleBuilderBase
from bootstack.widgets._impl.primitives import RadioToggle, CheckToggle, Frame, Label, Separator
from bootstack.widgets._impl.primitives.button import Button
from bootstack.widgets.types import Master
from bootstack.widgets._impl.composites.compositeframe import CompositeFrame, CompositeFrameKwargs
from bootstack.widgets._impl.mixins import CustomConfigMixin, configure_delegate


ContextMenuTrigger = Literal[
    'right-click', 'click', 'left-click', 'double-click',
    'shift-click', 'ctrl-click', 'control-click', 'manual',
]
"""Gesture that auto-shows a `ContextMenu` when the user interacts with the target widget.

Pass `None` to disable auto-binding and manage activation in caller code.
"""

ContextMenuItemResult = Button | CheckToggle | RadioToggle | Separator | str
"""Return type for ContextMenu item-add and item-lookup operations.

On Windows and Linux the result is the created widget. On macOS (native
`NSMenu` backend) the result is a string key since no per-item widget exists.
"""


# Sentinel for "argument not provided" so we can distinguish between
# "caller omitted target" (default to master) and "caller passed target=None
# explicitly" (no target — no positioning, no auto-trigger).
_TARGET_DEFAULT: Any = object()


class _CommandItemFrame(CompositeFrame):
    """Container frame for command items that delegates to the inner button.

    Uses CompositeFrame for automatic state propagation across children.
    """

    def __init__(self, master: Master, **kwargs: Unpack[CompositeFrameKwargs]):
        """Create a command item container frame."""
        self._button: Button | None = None  # Must be set before super().__init__
        super().__init__(master, **kwargs)

    def invoke(self):
        """Delegate invoke to the button."""
        if self._button:
            return self._button.invoke()

    def state(self, statespec=None):
        """Get or set state, propagating to button when setting."""
        if statespec is None:
            # Getter: return button state if available
            if self._button:
                return self._button.state()
            return super().state()
        else:
            # Setter: set state on self (for Composite propagation)
            # Button and label get state from Composite directly since they're registered
            return super().state(statespec)

    def configure(self, cnf=None, **kwargs):
        """Delegate configure to the button for common options."""
        if self._button:
            return self._button.configure(cnf, **kwargs)
        return super().configure(cnf, **kwargs)


class ContextMenuItem:
    """Data class for context menu items.

    Attributes:
        type: Type of menu item ('command', 'checkbutton', 'radiobutton', 'separator').
        kwargs: Additional keyword arguments for the item.
    """

    def __init__(self, type: str, **kwargs: Any) -> None:
        """Initialize a context menu item.

        Args:
            type: Type of menu item ('command', 'checkbutton', 'radiobutton', 'separator').
            **kwargs: Additional arguments passed to the widget.
        """
        self.type: str = type
        self.kwargs: dict[str, Any] = kwargs


class _ToplevelContextMenu(CustomConfigMixin):
    """Themed Toplevel-backed context menu (Win/Linux backend).

    Internal backend used by `ContextMenu` on Windows and Linux. Renders
    items as bootstack-styled widgets inside an overrideredirect Toplevel
    so theme tokens, density, and rich item types apply consistently.
    """

    def __init__(
            self,
            master: Master = None,
            minwidth: int = 150,
            width: int = None,
            minheight: int = None,
            height: int = None,
            target: Misc = None,
            anchor: AnchorPoint = 'nw',
            attach: AnchorPoint = 'se',
            offset: tuple[int, int] = None,
            hide_on_outside_click: bool = True,
            items: list[ContextMenuItem] = None,
            density: WidgetDensity = 'default',
            command: Callable = None,
    ):
        """Initialize the themed Toplevel backend.

        Args:
            master: Parent widget. If None, uses the default root window.
            minwidth: Minimum width for the menu in pixels. Default is 150.
            width: Fixed width for the menu in pixels. If None, uses minwidth.
            minheight: Minimum height for the menu in pixels. If None, auto-sizes.
            height: Fixed height for the menu in pixels. If None, auto-sizes to content.
            target: Target widget to attach the menu to. Used for relative positioning.
            anchor: Anchor point on the menu to align (e.g., 'nw', 'ne', 'sw', 'se', 'center').
            attach: Anchor point on the target to align to (same options as anchor).
            offset: Tuple (dx, dy) applied after alignment. Defaults to
                `(scale_from_source(10), 0)` to account for the focus-ring
                affordance baked into trigger button images, so attached menus
                align with the visible button border out of the box. Pass
                `(0, 0)` explicitly to position the menu at the exact anchor
                point with no offset.
            hide_on_outside_click: If True, menu hides when clicking outside.
                Default is True.
            items: List of ContextMenuItem objects to add initially.
            density: Item typography density ('default' or 'compact'). Items
                inherit this so they match the trigger widget's font size.
        """
        super().__init__()
        self._master = master
        self._target = target
        self._minwidth = minwidth
        self._width = width
        self._minheight = minheight
        self._height = height
        self._anchor = (anchor or 'nw').lower()
        self._attach = (attach or 'nw').lower()
        self._offset = offset if offset is not None else (BootstyleBuilderBase.scale_from_source(10), 0)
        self._hide_on_outside_click = hide_on_outside_click
        self._density = density
        self._command = command
        self._click_handler_id = None
        self._click_binding_root = None
        self._click_bind_after_id = None

        # Create toplevel window. This backend is selected on Win/Linux only;
        # Aqua dispatches to `_NativeContextMenu` to avoid the key-window
        # activation issues that affect a reused overrideredirect Toplevel
        # on macOS.
        self._toplevel = Toplevel(master)
        self._toplevel.withdraw()
        self._toplevel.overrideredirect(True)

        # Create frame with border and padding
        self._frame = Frame(
            self._toplevel,
            show_border=True,
            padding=4,
            surface='overlay'
        )
        self._frame.pack(fill='both', expand=True)

        # Configure size constraints
        if width:
            self._frame.configure(width=width)
        if height:
            self._frame.configure(height=height)

        # Set minimum size on toplevel
        if minwidth or minheight:
            self._toplevel.minsize(minwidth or 0, minheight or 0)

        # Track menu items by key with insertion order
        self._items: dict[str, Widget] = {}
        self._item_order: list[str] = []
        self._counter = 0  # For auto-generating keys
        self._highlighted_index = -1

        # Add initial items if provided
        if items:
            self.add_items(items)

        # Setup keyboard bindings
        self._setup_keyboard_bindings()

    def _generate_key(self) -> str:
        """Generate an auto key for an item."""
        key = f"item_{self._counter}"
        self._counter += 1
        return key

    def _resolve_key(self, key_or_index: str | int) -> str:
        """Resolve a key or index to a key.

        Args:
            key_or_index: Either a string key or integer index.

        Returns:
            The string key.

        Raises:
            KeyError: If key not found.
            IndexError: If index out of range.
        """
        if isinstance(key_or_index, int):
            try:
                return self._item_order[key_or_index]
            except IndexError as exc:
                raise IndexError(f"ContextMenu item index {key_or_index} out of range") from exc
        else:
            if key_or_index not in self._items:
                raise KeyError(f"No item with key '{key_or_index}'")
            return key_or_index

    def _register_item(self, key: str | None, widget: Widget) -> str:
        """Register an item with optional key, auto-generating if needed.

        Args:
            key: Optional key. Auto-generated if None.
            widget: The widget to register.

        Returns:
            The key used (either provided or auto-generated).

        Raises:
            ValueError: If key already exists.
        """
        if key is None:
            key = self._generate_key()

        if key in self._items:
            raise ValueError(f"Item with key '{key}' already exists")

        self._items[key] = widget
        self._item_order.append(key)
        return key

    def add_command(
            self,
            text: str = None,
            icon: str = None,
            command: Callable = None,
            disabled: bool = False,
            shortcut: str = None,
            key: str = None
    ) -> Button:
        """Add a command button to the menu.

        Args:
            text: Button text label.
            icon: Optional icon name. Uses 'empty' placeholder if None
                to maintain text alignment with items that have icons.
            command: Function to call when clicked.
            disabled: If True, the item is disabled and cannot be clicked.
            shortcut: Optional keyboard shortcut. Can be either:
                - A key registered with the Shortcuts service (e.g., "save")
                - A literal display string (e.g., "Ctrl+S")
                If a registered key is provided, the platform-appropriate
                display string is shown automatically.
            key: Optional unique identifier. Auto-generated if not provided.

        Returns:
            Button: The created Button widget.
        """
        # Resolve shortcut display text.
        # format_shortcut handles all three forms: registered key name,
        # modifier pattern ("Mod+S" → "Ctrl+S"), and literal pass-through.
        shortcut_display = format_shortcut(shortcut) if shortcut else None

        if shortcut_display:
            # Use CompositeFrame container for items with shortcuts
            # This handles state propagation (hover, pressed, focus) across children
            container = _CommandItemFrame(self._frame, variant='context-frame')
            container.pack(fill='x', padx=0, pady=0)

            btn = Button(
                container,
                text=text,
                icon=icon or 'empty',
                compound='left',
                variant='context-item',
                density=self._density,
                command=lambda: self._handle_item_click('command', text, command)
            )
            btn.pack(side='left', fill='x', expand=True)

            shortcut_label = Label(
                container,
                text=shortcut_display,
                variant='context-label',
                density=self._density,
                padding=(0, 0, 4, 0)
            )
            shortcut_label.pack(side='right')

            # Register children with CompositeFrame for state propagation
            container.register_composite(btn)
            container.register_composite(shortcut_label)

            container._button = btn
            if disabled:
                container.set_disabled(True)

            self._register_item(key, container)
            return btn
        else:
            # Simple button without shortcut
            btn = Button(
                self._frame,
                text=text,
                icon=icon or 'empty',
                compound='left',
                variant='context-item',
                density=self._density,
                command=lambda: self._handle_item_click('command', text, command)
            )
            if disabled:
                btn.state(['disabled'])
            btn.pack(fill='x', padx=0, pady=0)
            self._register_item(key, btn)
            return btn

    def add_checkbutton(
            self,
            text: str = None,
            value: bool = False,
            command: Callable = None,
            key: str = None
    ) -> CheckToggle:
        """Add a checkbutton to the menu.

        Args:
            text: Checkbutton text label.
            value: Initial checked state.
            command: Function to call when toggled.
            key: Optional unique identifier. Auto-generated if not provided.
        """
        var = BooleanVar(value=value)

        def on_toggle():
            self._handle_item_click('checkbutton', text, command, var.get())

        cb = CheckToggle(
            self._frame,
            text=text,
            variable=var,
            variant='context-check',
            density=self._density,
            command=on_toggle
        )
        cb.pack(fill='x', padx=0, pady=0)
        cb._variable = var  # Store reference to prevent garbage collection
        self._register_item(key, cb)
        return cb

    def add_radiobutton(
            self,
            text: str = None,
            value: Any = None,
            variable: StringVar | IntVar = None,
            command: Callable = None,
            icon: str = None,
            disabled: bool = False,
            key: str = None
    ) -> RadioToggle:
        """Add a radiobutton to the menu.

        Args:
            text: Radiobutton text label.
            value: Value to set when selected.
            variable: Tkinter Variable to link with.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            command: Function to call when selected.
            icon: Optional icon name rendered beside the label.
            disabled: If True, the item is dimmed and cannot be selected.
            key: Optional unique identifier. Auto-generated if not provided.
        """

        def on_select():
            self._handle_item_click('radiobutton', text, command, value)

        rb_kwargs: dict[str, Any] = {}
        if icon is not None:
            rb_kwargs['icon'] = icon
        rb = RadioToggle(
            self._frame,
            text=text,
            value=value,
            variable=variable,
            variant='context-radio',
            density=self._density,
            command=on_select,
            **rb_kwargs,
        )
        if disabled:
            rb.state(['disabled'])
        rb.pack(fill='x', padx=0, pady=0)
        self._register_item(key, rb)
        return rb

    def add_separator(self, key: str = None) -> Separator:
        """Add a horizontal separator to the menu.

        Args:
            key: Optional unique identifier. Auto-generated if not provided.

        Returns:
            Separator: The created Separator widget.
        """
        sep = Separator(self._frame, orient='horizontal')
        sep.pack(fill='x', padx=0, pady=3)
        self._register_item(key, sep)
        return sep

    def add_item(self, type: str, **kwargs: Any) -> ContextMenuItemResult:
        """Add a menu item based on type.

        Args:
            type: One of `'command'`, `'checkbutton'`, `'radiobutton'`, `'separator'`.
            **kwargs: Arguments passed to the appropriate add_* method.
        """
        if type == 'command':
            return self.add_command(**kwargs)
        elif type == 'checkbutton':
            return self.add_checkbutton(**kwargs)
        elif type == 'radiobutton':
            return self.add_radiobutton(**kwargs)
        elif type == 'separator':
            return self.add_separator(**kwargs)
        else:
            raise ValueError(f"Unknown item type: {type}")

    def add_items(self, items: list[ContextMenuItem]) -> None:
        """Add multiple items at once.

        Args:
            items: List of ContextMenuItem objects or dictionaries with 'type' and 'kwargs'.
        """
        for item in items:
            if isinstance(item, ContextMenuItem):
                self.add_item(item.type, **item.kwargs)
            elif isinstance(item, dict):
                item_type = item.get('type')
                kwargs = {k: v for k, v in item.items() if k != 'type'}
                self.add_item(item_type, **kwargs)

    def items(self, value=None):
        """Get or set the current menu items."""
        if value is None:
            return self._delegate_items(None)
        self._delegate_items(value)
        return None

    def keys(self) -> tuple[str, ...]:
        """Get all item keys in order.

        Returns:
            A tuple of all item keys in the order they were added.
        """
        return tuple(self._item_order)

    def insert_item(self, index: int, type: str, **kwargs: Any) -> ContextMenuItemResult:
        """Insert a new item at the given index.

        Args:
            index: Position to insert the item at.
            type: One of `'command'`, `'checkbutton'`, `'radiobutton'`, `'separator'`.
            **kwargs: Arguments passed to the appropriate add_* method.
        """
        before_key = self._item_order[index] if 0 <= index < len(self._item_order) else None
        before_widget = self._items[before_key] if before_key else None

        widget = self.add_item(type, **kwargs)

        if before_widget is None:
            return widget

        # Get the key of the just-added widget (last in order)
        new_key = self._item_order.pop()

        pack_info = widget.pack_info()
        widget.pack_forget()
        pack_info.pop('in', None)
        pack_info['before'] = before_widget
        widget.pack(**pack_info)

        # Insert key at correct position
        self._item_order.insert(index, new_key)
        return widget

    def item(self, key_or_index: str | int) -> ContextMenuItemResult:
        """Get a menu item by key or index.

        Args:
            key_or_index: The key (str) or index (int) of the item to retrieve.

        Raises:
            KeyError: If no item with the given key exists.
            IndexError: If the index is out of range.
        """
        key = self._resolve_key(key_or_index)
        return self._items[key]

    def remove_item(self, key_or_index: str | int) -> None:
        """Remove and destroy the item by key or index.

        Args:
            key_or_index: Key (str) or index (int) of the item to remove.
        """
        key = self._resolve_key(key_or_index)
        widget = self._items.pop(key)
        self._item_order.remove(key)

        try:
            widget.destroy()
        except TclError:
            pass
        return None

    def move_item(self, from_key_or_index: str | int, to_index: int) -> ContextMenuItemResult:
        """Reorder an existing item to a new index.

        Args:
            from_key_or_index: Key (str) or index (int) of the item to move.
            to_index: New index for the item.
        """
        key = self._resolve_key(from_key_or_index)
        widget = self._items[key]

        # Remove from current position in order
        self._item_order.remove(key)

        pack_info = widget.pack_info()
        widget.pack_forget()

        # Clamp destination to valid bounds
        if to_index < 0:
            to_index = 0
        if to_index > len(self._item_order):
            to_index = len(self._item_order)

        # Insert at new position
        self._item_order.insert(to_index, key)
        before_key = self._item_order[to_index + 1] if to_index + 1 < len(self._item_order) else None
        before_widget = self._items[before_key] if before_key else None

        pack_info.pop('in', None)
        pack_info.pop('in_', None)
        pack_info.pop('before', None)
        pack_info.pop('after', None)
        if before_widget:
            pack_info['before'] = before_widget
        widget.pack(in_=self._frame, **pack_info)
        return widget

    def configure_item(self, key_or_index: str | int, option: str | None = None, **kwargs: Any) -> Any:
        """Configure an individual menu item by key or index.

        Args:
            key_or_index: Key (str) or index (int) of the item to configure.
            option: Optional option name to query (getter path).
            **kwargs: Option values to set (setter path).

        Returns:
            - When called with no kwargs and no option: full option map for the item.
            - When called with option only: a 5-tuple matching tkinter's configure.
            - When called with kwargs: the result of the underlying widget's configure.
        """
        key = self._resolve_key(key_or_index)
        widget = self._items[key]

        # Getter: all options
        if option is None and not kwargs:
            return widget.configure()

        # Getter: single option
        if option is not None and not kwargs:
            return widget.configure(option)

        # Setter path
        return widget.configure(**kwargs)

    def show(self, position: tuple[int, int] = None) -> None:
        """Show the context menu.

        Args:
            position: Optional screen coordinate (x, y) to align to. If provided,
                the menu's anchor will align to this point. Negative x/y are
                treated as offsets from the screen's right/bottom.
        """
        # Update geometry before showing
        self._toplevel.update_idletasks()

        # Determine position
        pos = self._compute_position(position)
        if pos:
            self._toplevel.geometry(f"+{pos[0]}+{pos[1]}")

        # Show the menu. Setting topmost ensures the popup rises above any
        # parent window that has -topmost True (e.g. a screenshot capture harness).
        self._toplevel.deiconify()
        self._toplevel.attributes('-topmost', True)
        self._toplevel.lift()
        self._toplevel.focus_force()

        # Start with no item highlighted (keyboard nav will highlight on first arrow key)
        self._highlighted_index = -1

        # Setup click outside handler if enabled
        if self._hide_on_outside_click:
            self._setup_click_outside_handler()

    def _setup_keyboard_bindings(self) -> None:
        """Setup keyboard navigation bindings on the toplevel."""
        self._toplevel.bind('<Escape>', lambda e: self.hide())
        self._toplevel.bind('<Down>', self._on_arrow_down)
        self._toplevel.bind('<Up>', self._on_arrow_up)
        self._toplevel.bind('<Return>', self._on_enter)
        self._toplevel.bind('<KP_Enter>', self._on_enter)

    def _get_actionable_items(self) -> list:
        """Return list of items that can be navigated to (excludes separators)."""
        return [self._items[key] for key in self._item_order if not isinstance(self._items[key], Separator)]

    def _on_arrow_down(self, event) -> str:
        """Handle arrow down key."""
        actionable = self._get_actionable_items()
        if not actionable:
            return 'break'

        # Find next actionable item
        current = self._highlighted_index
        next_idx = current + 1 if current < len(actionable) - 1 else 0
        self._update_highlight(next_idx)
        return 'break'

    def _on_arrow_up(self, event) -> str:
        """Handle arrow up key."""
        actionable = self._get_actionable_items()
        if not actionable:
            return 'break'

        # Find previous actionable item
        current = self._highlighted_index
        prev_idx = current - 1 if current > 0 else len(actionable) - 1
        self._update_highlight(prev_idx)
        return 'break'

    def _on_enter(self, event) -> str:
        """Handle enter key to activate highlighted item."""
        actionable = self._get_actionable_items()
        if not actionable or self._highlighted_index < 0:
            return 'break'

        if 0 <= self._highlighted_index < len(actionable):
            item = actionable[self._highlighted_index]
            # Simulate a click by invoking the button
            item.invoke()
        return 'break'

    def _update_highlight(self, new_index: int) -> None:
        """Update the highlighted item."""
        actionable = self._get_actionable_items()
        if not actionable:
            self._highlighted_index = -1
            return

        # Clamp index
        new_index = max(0, min(new_index, len(actionable) - 1))

        # Remove highlight from old item
        if 0 <= self._highlighted_index < len(actionable):
            actionable[self._highlighted_index].state(['!focus'])

        # Add highlight to new item
        actionable[new_index].state(['focus'])
        self._highlighted_index = new_index

    def hide(self) -> None:
        """Hide the context menu."""
        # Unbind click handler first
        self._cancel_click_outside_after()
        self._unbind_click_outside_handler()

        # Clear highlight state
        self._clear_highlight()

        if self._toplevel.winfo_exists():
            self._toplevel.withdraw()

    def _clear_highlight(self) -> None:
        """Clear the highlight from the current item."""
        actionable = self._get_actionable_items()
        if 0 <= self._highlighted_index < len(actionable):
            actionable[self._highlighted_index].state(['!focus'])
        self._highlighted_index = -1

    def destroy(self) -> None:
        """Destroy the context menu and cleanup resources."""
        # Unbind click handler
        self._cancel_click_outside_after()
        self._unbind_click_outside_handler()

        # Destroy toplevel
        if self._toplevel.winfo_exists():
            self._toplevel.destroy()

    def _handle_item_click(self, type: str, text: str, command: Callable = None, value: Any = None) -> None:
        """Handle item click events.

        Args:
            type: Type of item clicked.
            text: Text of the item.
            command: Command to execute.
            value: Value associated with the item.
        """
        # Prepare event data
        data = {
            'type': type,
            'text': text,
            'value': value
        }

        # Call registered callback
        if self._command:
            self._command(data)

        # Execute item command
        if command:
            command()

        # Hide menu after item click
        self.hide()

    def _compute_position(self, position: tuple[int, int] | None) -> tuple[int, int] | None:
        """Compute screen coordinates for the menu based on anchor/attach/offset."""

        def anchor_offsets(key: str, width: int, height: int) -> tuple[float, float]:
            table = {
                'nw': (0, 0),
                'n': (width / 2, 0),
                'ne': (width, 0),
                'w': (0, height / 2),
                'center': (width / 2, height / 2),
                'e': (width, height / 2),
                'sw': (0, height),
                's': (width / 2, height),
                'se': (width, height),
            }
            if key not in table:
                raise ValueError(f"Invalid anchor '{key}'. Use one of: {', '.join(table.keys())}")
            return table[key]

        # Ensure geometry is up to date for accurate size
        self._toplevel.update_idletasks()

        menu_w = self._toplevel.winfo_reqwidth()
        menu_h = self._toplevel.winfo_reqheight()

        # Base point: from provided position or target attach
        base_x = base_y = None

        if position is not None:
            base_x, base_y = position
        elif self._target and self._target.winfo_exists():
            self._target.update_idletasks()
            target_w = self._target.winfo_width()
            target_h = self._target.winfo_height()
            base_x = self._target.winfo_rootx()
            base_y = self._target.winfo_rooty()
            attach_dx, attach_dy = anchor_offsets(self._attach, target_w, target_h)
            base_x += attach_dx
            base_y += attach_dy
        else:
            return None

        menu_dx, menu_dy = anchor_offsets(self._anchor, menu_w, menu_h)
        final_x = int(base_x - menu_dx + self._offset[0])
        final_y = int(base_y - menu_dy + self._offset[1])

        # Flip vertically when the menu would overflow the screen bottom and
        # there's room above the target. Matches Tk combobox PlacePopdown.
        if self._target is not None and self._target.winfo_exists():
            screen_h = self._toplevel.winfo_screenheight()
            if final_y + menu_h > screen_h:
                target_top = self._target.winfo_rooty()
                alt_y = target_top - menu_h - self._offset[1]
                if alt_y >= 0:
                    final_y = alt_y
        return final_x, final_y

    def _setup_click_outside_handler(self) -> None:
        """Setup handler to hide menu when clicking outside."""

        def on_click(event):
            # Don't process if menu is not visible
            if not self._toplevel.winfo_viewable():
                return

            # Check if click is inside the menu
            try:
                x, y = event.x_root, event.y_root
                tx = self._toplevel.winfo_rootx()
                ty = self._toplevel.winfo_rooty()
                tw = self._toplevel.winfo_width()
                th = self._toplevel.winfo_height()

                # Click is outside if coordinates are not within bounds
                if not (tx <= x <= tx + tw and ty <= y <= ty + th):
                    self.hide()
            except TclError:
                # If the menu has been torn down, ensure it is hidden
                self.hide()

        def bind_click():
            # Clear the pending after id once we run
            self._click_bind_after_id = None

            # Skip binding if the menu is already hidden
            if not (self._toplevel.winfo_exists() and self._toplevel.winfo_viewable()):
                return

            if self._toplevel.winfo_exists():
                self._unbind_click_outside_handler()
                root = self._get_binding_root()
                if root and root.winfo_exists():
                    self._click_binding_root = root
                    self._click_handler_id = root.bind('<Button-1>', on_click, add='+')

        # Delay binding to avoid capturing the click that shows the menu
        self._cancel_click_outside_after()
        self._click_bind_after_id = self._toplevel.after(100, bind_click)

    def _get_binding_root(self) -> Widget | None:
        """Return the widget to bind click-outside events to."""
        candidate = self._target or self._master or self._toplevel.master
        if candidate:
            try:
                return candidate.winfo_toplevel()
            except TclError:
                return None
        return None

    def _unbind_click_outside_handler(self) -> None:
        """Remove the click-outside binding if present."""
        if not self._click_handler_id or not self._click_binding_root:
            return

        try:
            if self._click_binding_root.winfo_exists():
                self._click_binding_root.unbind('<Button-1>', self._click_handler_id)
        except TclError:
            pass
        finally:
            self._click_handler_id = None
            self._click_binding_root = None

    def _cancel_click_outside_after(self) -> None:
        """Cancel any scheduled click-outside binding."""
        if self._click_bind_after_id and self._toplevel.winfo_exists():
            try:
                self._toplevel.after_cancel(self._click_bind_after_id)
            except TclError:
                pass
        self._click_bind_after_id = None

    # ----- Configuration delegates -------------------------------------------------

    @configure_delegate('command')
    def _delegate_command(self, value: Callable | None = None):
        """Get or set the item-click callback."""
        if value is None and not self._command:
            return self._command
        self._command = value
        return None

    @configure_delegate('minwidth')
    def _delegate_minwidth(self, value: int | None):
        """Get or set the minimum width."""
        if value is None:
            return self._minwidth
        self._minwidth = value
        return self._toplevel.minsize(value or 0, self._minheight or 0)

    @configure_delegate('minheight')
    def _delegate_minheight(self, value: int | None):
        """Get or set the minimum height."""
        if value is None:
            return self._minheight
        self._minheight = value
        return self._toplevel.minsize(self._minwidth or 0, value or 0)

    @configure_delegate('width')
    def _delegate_width(self, value: int | None):
        """Get or set the fixed width."""
        if value is None:
            return self._width
        self._width = value
        return self._frame.configure(width=value if value is not None else '')

    @configure_delegate('height')
    def _delegate_height(self, value: int | None):
        """Get or set the fixed height."""
        if value is None:
            return self._height
        self._height = value
        return self._frame.configure(height=value if value is not None else '')

    @configure_delegate('anchor')
    def _delegate_anchor(self, value: str | None):
        """Get or set the menu anchor."""
        if value is None:
            return self._anchor
        self._anchor = (value or 'nw').lower()
        return None

    @configure_delegate('attach')
    def _delegate_attach(self, value: str | None):
        """Get or set the target attach anchor."""
        if value is None:
            return self._attach
        self._attach = (value or 'nw').lower()
        return None

    @configure_delegate('offset')
    def _delegate_offset(self, value: tuple[int, int] | None):
        """Get or set the positional offset."""
        if value is None:
            return self._offset
        try:
            dx, dy = value  # type: ignore[misc]
        except Exception:
            dx, dy = (0, 0)
        self._offset = (dx, dy)
        return None

    @configure_delegate('hide_on_outside_click')
    def _delegate_hide_on_outside_click(self, value: bool | None):
        """Get or set outside-click hide behavior."""
        if value is None:
            return self._hide_on_outside_click
        self._hide_on_outside_click = bool(value)
        return None

    @configure_delegate('target')
    def _delegate_target(self, value: Misc | None):
        """Get or set the target widget used for positioning."""
        if value is None:
            return self._target
        self._target = value
        return None

    @configure_delegate('items')
    def _delegate_items(self, value: list[ContextMenuItem] | None):
        """Get or replace the menu items."""
        if value is None:
            # Return items in order
            return [self._items[key] for key in self._item_order]

        # Destroy existing widgets before replacing
        for widget in self._items.values():
            try:
                widget.destroy()
            except TclError:
                pass
        self._items = {}
        self._item_order = []
        self._counter = 0
        self.add_items(value)
        return None


class _NativeContextMenu(CustomConfigMixin):
    """Native `tk.Menu`-backed context menu (Aqua/Windows backend).

    Internal backend used by `ContextMenu` on macOS so the popup is a real
    NSMenu — sidesteps the key-window/activation issues that affect a
    reused overrideredirect Toplevel. Theming follows the system menu look.
    Menus are text-only here (no icons) by native convention; an `icon=`
    argument is accepted for cross-backend API parity but ignored.
    """

    def __init__(
            self,
            master: Master = None,
            minwidth: int = 150,
            width: int = None,
            minheight: int = None,
            height: int = None,
            target: Misc = None,
            anchor: AnchorPoint = 'nw',
            attach: AnchorPoint = 'se',
            offset: tuple[int, int] = None,
            hide_on_outside_click: bool = True,
            items: list[ContextMenuItem] = None,
            density: WidgetDensity = 'default',
            command: Callable = None,
    ):
        """Initialize the native tk.Menu backend.

        Args mirror the themed backend so the public `ContextMenu` API is
        identical across platforms. Several options (`minwidth`, `width`,
        `height`, `hide_on_outside_click`, `density`) are stored for
        `cget` parity but have no effect — the system menu controls
        sizing, dismissal, and typography on the host platform.
        """
        import tkinter as tk

        super().__init__()
        self._master = master
        self._target = target
        self._minwidth = minwidth
        self._width = width
        self._minheight = minheight
        self._height = height
        self._anchor = (anchor or 'nw').lower()
        self._attach = (attach or 'nw').lower()
        # Default offset matches the themed backend so consumers that pass
        # an explicit offset for chrome alignment don't need a Mac-specific
        # branch. The native menu still clamps to screen edges itself.
        self._offset = offset if offset is not None else (BootstyleBuilderBase.scale_from_source(10), 0)
        self._hide_on_outside_click = hide_on_outside_click
        self._density = density
        self._command = command

        # Native tk.Menu (NSMenu on macOS). Unlike the menu BAR (text-only by
        # convention), a context menu is app content, so icons are rendered
        # here — re-colored on theme/appearance change (see `_on_theme_changed`).
        self._menu = tk.Menu(master, tearoff=0)

        # Item tracking by key with insertion order; specs are kept so we
        # can rebuild the menu on insert/move (tk.Menu has no atomic move).
        self._item_specs: dict[str, dict] = {}
        self._item_order: list[str] = []
        self._counter = 0

        # Strong refs so Tk objects the menu holds aren't GC'd: variables for
        # check/radio items, and PhotoImages for item icons.
        self._var_refs: dict[str, Any] = {}
        self._icon_refs: list[Any] = []

        # Re-render icons when the theme or macOS appearance changes so their
        # color tracks the menu text color. Bound on the root; ids kept for
        # clean teardown in destroy().
        self._theme_binds: list[tuple[str, str]] = []
        self._bind_theme_tracking()

        if items:
            self.add_items(items)

    # ----- Internal helpers -------------------------------------------------

    def _generate_key(self) -> str:
        key = f"item_{self._counter}"
        self._counter += 1
        return key

    def _resolve_key(self, key_or_index: str | int) -> str:
        if isinstance(key_or_index, int):
            try:
                return self._item_order[key_or_index]
            except IndexError as exc:
                raise IndexError(
                    f"ContextMenu item index {key_or_index} out of range"
                ) from exc
        if key_or_index not in self._item_specs:
            raise KeyError(f"No item with key '{key_or_index}'")
        return key_or_index

    def _key_to_index(self, key: str) -> int:
        return self._item_order.index(key)

    def _resolve_label(self, text: str | None) -> str:
        """Translate a semantic message key; pass plain text through unchanged."""
        if not text:
            return ''
        try:
            from bootstack.i18n import MessageCatalog

            return MessageCatalog.translate(text) or text
        except Exception:
            return text

    # ----- Icon rendering (context menus only — not the menu bar) ------------

    def _menu_icon_color(self) -> str:
        """Foreground color for item icons.

        On Aqua, NSMenu uses system appearance regardless of the app theme, so
        icons must match the system text color (which Tk keeps in sync with
        macOS light/dark mode). Elsewhere the app theme's foreground is right.
        """
        try:
            winsys = self._menu.tk.call('tk', 'windowingsystem')
        except TclError:
            winsys = None
        if winsys == 'aqua':
            try:
                r, g, b = self._menu.winfo_rgb('systemTextColor')
                return f'#{r >> 8:02x}{g >> 8:02x}{b >> 8:02x}'
            except TclError:
                pass
        from bootstack.style.style import get_style
        return get_style().style_builder.color('foreground')

    def _resolve_icon(self, icon_spec: Any) -> Any:
        """Render an icon spec to a themed PhotoImage, or `None`.

        Accepts a glyph name or `{'name', 'size'}`. The returned image is also
        retained (strong ref) so Tk doesn't GC it while the menu holds it.
        """
        if not icon_spec or icon_spec == 'empty':
            return None
        if isinstance(icon_spec, dict):
            name, size = icon_spec.get('name'), icon_spec.get('size')
        else:
            name, size = icon_spec, None
        if not name:
            return None
        if size is None:
            try:
                from tkinter import font as _tkfont
                size = _tkfont.nametofont('TkMenuFont').metrics('linespace')
            except Exception:
                size = 16
        try:
            from bootstack._core.images import Image as _ImageService
            photo = _ImageService.get_icon(name, size, self._menu_icon_color())
        except Exception:
            return None
        self._icon_refs.append(photo)
        return photo

    def _bind_theme_tracking(self) -> None:
        """Bind theme / macOS-appearance changes to re-render item icons."""
        try:
            root = self._menu.winfo_toplevel()
        except TclError:
            return
        for seq in ('<<ThemeChanged>>', '<<TkSystemAppearanceChanged>>'):
            try:
                func_id = root.bind(seq, self._on_theme_changed, add='+')
                self._theme_binds.append((seq, func_id))
            except TclError:
                pass

    def _on_theme_changed(self, event: Any = None) -> None:
        """Re-render the menu so icon colors track the new theme/appearance."""
        if self._item_order:
            self._rebuild_menu()

    def _wrap_command(self, type_: str, text: str | None,
                      command: Callable | None, value: Any = None) -> Callable:
        def fire():
            if self._command:
                self._command({
                    'type': type_,
                    'text': text,
                    'value': value,
                })
            if command:
                command()
        return fire

    def _resolve_shortcut(self, shortcut: str | None) -> str | None:
        """Native-menu accelerator for `shortcut`.

        Accepts a registered key, a modifier pattern (`'Mod+S'`, `'F5'`), or a
        literal string. Uses the Tk-Aqua *word* form (`'Command+S'`) so the
        native menu renders the ⌘ glyph AND the key — a pre-symbolized display
        would drop the key. See
        `bootstack._runtime.shortcuts.tk_aqua_accelerator`.
        """
        if not shortcut:
            return None
        from bootstack._runtime.shortcuts import tk_aqua_accelerator
        return tk_aqua_accelerator(shortcut) or None

    # ----- Public API mirroring the themed backend ---------------------------

    def add_command(
            self,
            text: str = None,
            icon: str = None,
            command: Callable = None,
            disabled: bool = False,
            shortcut: str = None,
            key: str = None,
    ) -> str:
        """Add a command. Returns the item key (no widget on this backend)."""
        key = key or self._generate_key()
        if key in self._item_specs:
            raise ValueError(f"Item with key '{key}' already exists")

        accelerator = self._resolve_shortcut(shortcut)

        opts: dict[str, Any] = {
            'label': self._resolve_label(text),
            'command': self._wrap_command('command', text, command),
        }
        photo = self._resolve_icon(icon)
        if photo is not None:
            opts['image'] = photo
            opts['compound'] = 'left'
        if accelerator:
            opts['accelerator'] = accelerator
        if disabled:
            opts['state'] = 'disabled'

        self._menu.add_command(**opts)

        self._item_specs[key] = {
            'type': 'command',
            'text': text,
            'icon': icon,
            'command': command,
            'disabled': disabled,
            'shortcut': shortcut,
        }
        self._item_order.append(key)
        return key

    def add_checkbutton(
            self,
            text: str = None,
            value: bool = False,
            command: Callable = None,
            key: str = None,
    ) -> str:
        key = key or self._generate_key()
        if key in self._item_specs:
            raise ValueError(f"Item with key '{key}' already exists")

        var = BooleanVar(value=value)
        self._var_refs[key] = var

        def on_toggle():
            if self._command:
                self._command({
                    'type': 'checkbutton',
                    'text': text,
                    'value': var.get(),
                })
            if command:
                command()

        self._menu.add_checkbutton(
            label=self._resolve_label(text), variable=var, command=on_toggle,
        )
        self._item_specs[key] = {
            'type': 'checkbutton',
            'text': text,
            'value': value,
            'command': command,
        }
        self._item_order.append(key)
        return key

    def add_radiobutton(
            self,
            text: str = None,
            value: Any = None,
            variable: StringVar | IntVar = None,
            command: Callable = None,
            icon: str = None,
            disabled: bool = False,
            key: str = None,
    ) -> str:
        key = key or self._generate_key()
        if key in self._item_specs:
            raise ValueError(f"Item with key '{key}' already exists")

        if variable is None:
            variable = StringVar()
        # Always retain a strong ref; if the caller owns the variable, this
        # is a harmless extra reference.
        self._var_refs[key] = variable

        def on_select():
            if self._command:
                self._command({
                    'type': 'radiobutton',
                    'text': text,
                    'value': value,
                })
            if command:
                command()

        opts: dict[str, Any] = {
            'label': self._resolve_label(text),
            'variable': variable,
            'value': value,
            'command': on_select,
        }
        photo = self._resolve_icon(icon)
        if photo is not None:
            opts['image'] = photo
            opts['compound'] = 'left'
        if disabled:
            opts['state'] = 'disabled'

        self._menu.add_radiobutton(**opts)

        self._item_specs[key] = {
            'type': 'radiobutton',
            'text': text,
            'value': value,
            'variable': variable,
            'command': command,
            'icon': icon,
            'disabled': disabled,
        }
        self._item_order.append(key)
        return key

    def add_separator(self, key: str = None) -> str:
        key = key or self._generate_key()
        if key in self._item_specs:
            raise ValueError(f"Item with key '{key}' already exists")
        self._menu.add_separator()
        self._item_specs[key] = {'type': 'separator'}
        self._item_order.append(key)
        return key

    def add_item(self, type: str, **kwargs: Any) -> str:
        if type == 'command':
            return self.add_command(**kwargs)
        if type == 'checkbutton':
            return self.add_checkbutton(**kwargs)
        if type == 'radiobutton':
            return self.add_radiobutton(**kwargs)
        if type == 'separator':
            return self.add_separator(**kwargs)
        raise ValueError(f"Unknown item type: {type}")

    def add_items(self, items: list[ContextMenuItem]) -> None:
        for item in items:
            if isinstance(item, ContextMenuItem):
                self.add_item(item.type, **item.kwargs)
            elif isinstance(item, dict):
                item_type = item.get('type')
                kwargs = {k: v for k, v in item.items() if k != 'type'}
                self.add_item(item_type, **kwargs)

    def items(self, value=None):
        if value is None:
            return self._delegate_items(None)
        self._delegate_items(value)
        return None

    def keys(self) -> tuple[str, ...]:
        return tuple(self._item_order)

    def insert_item(self, index: int, type: str, **kwargs: Any) -> str:
        # Append, then reorder + rebuild — tk.Menu has no atomic move op
        # that preserves command bindings cleanly across insert points.
        new_key = self.add_item(type, **kwargs)
        self._item_order.remove(new_key)
        if index < 0:
            index = 0
        if index > len(self._item_order):
            index = len(self._item_order)
        self._item_order.insert(index, new_key)
        self._rebuild_menu()
        return new_key

    def item(self, key_or_index: str | int) -> dict:
        """Return the spec dict for an item.

        Note: native backend has no per-item widget. The returned dict is
        the original spec passed to `add_*` — useful for inspection but
        not a Tk widget. Mutating it does not affect the rendered menu.
        """
        key = self._resolve_key(key_or_index)
        return self._item_specs[key]

    def remove_item(self, key_or_index: str | int) -> None:
        key = self._resolve_key(key_or_index)
        idx = self._key_to_index(key)
        try:
            self._menu.delete(idx)
        except TclError:
            pass
        self._item_order.remove(key)
        self._item_specs.pop(key, None)
        self._var_refs.pop(key, None)
        return None

    def move_item(self, from_key_or_index: str | int, to_index: int) -> dict:
        key = self._resolve_key(from_key_or_index)
        self._item_order.remove(key)
        if to_index < 0:
            to_index = 0
        if to_index > len(self._item_order):
            to_index = len(self._item_order)
        self._item_order.insert(to_index, key)
        self._rebuild_menu()
        return self._item_specs[key]

    def configure_item(self, key_or_index: str | int,
                       option: str | None = None, **kwargs: Any) -> Any:
        key = self._resolve_key(key_or_index)
        idx = self._key_to_index(key)
        if option is None and not kwargs:
            return self._menu.entryconfigure(idx)
        if option is not None and not kwargs:
            return self._menu.entryconfigure(idx, option)
        return self._menu.entryconfigure(idx, **kwargs)

    def show(self, position: tuple[int, int] = None) -> None:
        x, y = self._compute_position(position)
        try:
            self._menu.tk_popup(x, y)
        finally:
            try:
                self._menu.grab_release()
            except TclError:
                pass

    def hide(self) -> None:
        try:
            self._menu.unpost()
        except TclError:
            pass

    def destroy(self) -> None:
        # Unbind the theme/appearance handlers so they don't fire on a torn-
        # down menu after the next theme change.
        if self._theme_binds:
            try:
                root = self._menu.winfo_toplevel()
                for seq, func_id in self._theme_binds:
                    try:
                        root.unbind(seq, func_id)
                    except TclError:
                        pass
            except TclError:
                pass
            self._theme_binds = []
        try:
            self._menu.destroy()
        except TclError:
            pass

    # ----- Internal: full menu rebuild ---------------------------------------

    def _rebuild_menu(self) -> None:
        """Tear down and re-add all entries from stored specs.

        Used by `insert_item` and `move_item` since tk.Menu offers no
        atomic reorder.
        """
        try:
            last = self._menu.index('end')
        except TclError:
            last = None
        if last is not None:
            try:
                self._menu.delete(0, last)
            except TclError:
                pass

        # Icons are re-resolved below with the current menu color, so drop the
        # old PhotoImage refs (a fresh set is collected as entries are re-added).
        self._icon_refs = []

        for key in self._item_order:
            spec = self._item_specs[key]
            type_ = spec['type']
            if type_ == 'separator':
                self._menu.add_separator()
                continue

            label = self._resolve_label(spec.get('text'))
            text = spec.get('text')

            if type_ == 'command':
                opts: dict[str, Any] = {
                    'label': label,
                    'command': self._wrap_command(
                        'command', text, spec.get('command'),
                    ),
                }
                photo = self._resolve_icon(spec.get('icon'))
                if photo is not None:
                    opts['image'] = photo
                    opts['compound'] = 'left'
                accelerator = self._resolve_shortcut(spec.get('shortcut'))
                if accelerator:
                    opts['accelerator'] = accelerator
                if spec.get('disabled'):
                    opts['state'] = 'disabled'
                self._menu.add_command(**opts)
            elif type_ == 'checkbutton':
                var = self._var_refs[key]
                command = spec.get('command')

                def on_toggle(_var=var, _text=text, _cmd=command):
                    if self._command:
                        self._command({
                            'type': 'checkbutton',
                            'text': _text,
                            'value': _var.get(),
                        })
                    if _cmd:
                        _cmd()

                self._menu.add_checkbutton(
                    label=label, variable=var, command=on_toggle,
                )
            elif type_ == 'radiobutton':
                var = spec.get('variable') or self._var_refs.get(key)
                value = spec.get('value')
                command = spec.get('command')

                def on_select(_text=text, _value=value, _cmd=command):
                    if self._command:
                        self._command({
                            'type': 'radiobutton',
                            'text': _text,
                            'value': _value,
                        })
                    if _cmd:
                        _cmd()

                radio_opts: dict[str, Any] = {
                    'label': label,
                    'variable': var,
                    'value': value,
                    'command': on_select,
                }
                photo = self._resolve_icon(spec.get('icon'))
                if photo is not None:
                    radio_opts['image'] = photo
                    radio_opts['compound'] = 'left'
                self._menu.add_radiobutton(**radio_opts)

    def _compute_position(self, position: tuple[int, int] | None) -> tuple[int, int]:
        """Resolve the screen-coordinate target for `tk_popup`.

        Mirrors the themed backend's anchor/attach/offset semantics, but
        without the menu-size step (the native menu auto-positions). When
        `position` is given, anchor/attach are ignored and only `offset`
        applies, matching the themed backend behavior.
        """
        if position is not None:
            return int(position[0] + self._offset[0]), int(position[1] + self._offset[1])

        if self._target and self._target.winfo_exists():
            self._target.update_idletasks()
            target_w = self._target.winfo_width()
            target_h = self._target.winfo_height()
            base_x = self._target.winfo_rootx()
            base_y = self._target.winfo_rooty()
            attach_table = {
                'nw': (0, 0),
                'n': (target_w / 2, 0),
                'ne': (target_w, 0),
                'w': (0, target_h / 2),
                'center': (target_w / 2, target_h / 2),
                'e': (target_w, target_h / 2),
                'sw': (0, target_h),
                's': (target_w / 2, target_h),
                'se': (target_w, target_h),
            }
            dx, dy = attach_table.get(self._attach, (0, 0))
            return (
                int(base_x + dx + self._offset[0]),
                int(base_y + dy + self._offset[1]),
            )

        return 0, 0

    # ----- Configuration delegates -------------------------------------------

    @configure_delegate('command')
    def _delegate_command(self, value: Callable | None = None):
        """Get or set the item-click callback."""
        if value is None and not self._command:
            return self._command
        self._command = value
        return None

    @configure_delegate('minwidth')
    def _delegate_minwidth(self, value: int | None):
        if value is None:
            return self._minwidth
        self._minwidth = value
        return None

    @configure_delegate('minheight')
    def _delegate_minheight(self, value: int | None):
        if value is None:
            return self._minheight
        self._minheight = value
        return None

    @configure_delegate('width')
    def _delegate_width(self, value: int | None):
        if value is None:
            return self._width
        self._width = value
        return None

    @configure_delegate('height')
    def _delegate_height(self, value: int | None):
        if value is None:
            return self._height
        self._height = value
        return None

    @configure_delegate('anchor')
    def _delegate_anchor(self, value: str | None):
        if value is None:
            return self._anchor
        self._anchor = (value or 'nw').lower()
        return None

    @configure_delegate('attach')
    def _delegate_attach(self, value: str | None):
        if value is None:
            return self._attach
        self._attach = (value or 'nw').lower()
        return None

    @configure_delegate('offset')
    def _delegate_offset(self, value: tuple[int, int] | None):
        if value is None:
            return self._offset
        try:
            dx, dy = value  # type: ignore[misc]
        except Exception:
            dx, dy = (0, 0)
        self._offset = (dx, dy)
        return None

    @configure_delegate('hide_on_outside_click')
    def _delegate_hide_on_outside_click(self, value: bool | None):
        if value is None:
            return self._hide_on_outside_click
        self._hide_on_outside_click = bool(value)
        return None

    @configure_delegate('target')
    def _delegate_target(self, value: Misc | None):
        if value is None:
            return self._target
        self._target = value
        return None

    @configure_delegate('items')
    def _delegate_items(self, value: list | None):
        if value is None:
            # Return spec dicts in order (no widgets exist on this backend)
            return [self._item_specs[key] for key in self._item_order]

        # Replace all items
        try:
            last = self._menu.index('end')
            if last is not None:
                self._menu.delete(0, last)
        except TclError:
            pass
        self._item_specs = {}
        self._item_order = []
        self._counter = 0
        self._var_refs = {}
        self._icon_refs = []
        self.add_items(value)
        return None


class ContextMenu:
    """Public ContextMenu — dispatches to a platform-appropriate backend.

    On macOS this materializes as a native `tk.Menu` (NSMenu) so popups
    integrate with the system, dodging the key-window/activation issues
    that affect a reused overrideredirect Toplevel on Aqua. On Windows
    and Linux it uses the themed Toplevel-backed implementation so theme
    tokens, density, and rich item types apply consistently.

    The public API is identical across backends. Consumers should not
    rely on `item()` returning a Tk widget — on the native backend it
    returns the original spec dict, since no per-item widget exists.
    """

    def __init__(
            self,
            master: Master = None,
            minwidth: int = 150,
            width: int = None,
            minheight: int = None,
            height: int = None,
            target: Misc = _TARGET_DEFAULT,
            anchor: AnchorPoint = 'nw',
            attach: AnchorPoint = 'se',
            offset: tuple[int, int] = None,
            hide_on_outside_click: bool = True,
            items: list[ContextMenuItem] = None,
            density: WidgetDensity = 'default',
            trigger: ContextMenuTrigger | None = 'right-click',
            command: Callable = None,
    ):
        """
        Args:
            master: Parent widget. If None, uses the default root window.
            minwidth: Minimum width of the menu popup in pixels. Default 150.
            width: Fixed width of the menu popup. If None, sizes to content.
            minheight: Minimum height of the menu popup in pixels.
            height: Fixed height of the menu popup in pixels.
            target: Widget the menu is attached to for positioning and
                auto-binding. Defaults to `master`. Pass `None` to opt out
                of auto-positioning (e.g. when calling `show(position=(x, y))`
                with cursor-driven coordinates).
            anchor: Corner of the menu aligned to the attach point. Default `'nw'`.
            attach: Corner of the target widget used as the attach point. Default `'se'`.
            offset: `(x, y)` pixel offset from the attach point.
            hide_on_outside_click: Auto-hide when clicking outside the menu. Default True.
            items: Initial list of menu items.
            density: Widget density — `'default'` or `'compact'`.
            trigger: Gesture that auto-shows the menu on the target widget.
                `'right-click'` (default) — platform right-click (`<Button-3>` on
                Win/Linux; `<Button-2>` and `<Control-Button-1>` on macOS).
                `'click'` / `'left-click'` — `<Button-1>`.
                `'double-click'` — `<Double-Button-1>`.
                `'shift-click'` — `<Shift-Button-1>`.
                `'ctrl-click'` / `'control-click'` — `<Control-Button-1>`.
                `None` or `'manual'` — no auto-binding; caller manages activation.
            command: Callback invoked when any menu item is clicked. Receives a
                dict with keys `type` (str), `text` (str), and `value` (Any).
                Single-slot — assigning a new value via `configure(command=...)`
                replaces the previous callback. Pass `None` to clear.
        """
        # Default target to master when omitted; explicit `None` opts out.
        if target is _TARGET_DEFAULT:
            target = master

        winsys = None
        probe = master if master is not None else target
        if probe is not None:
            try:
                winsys = probe.tk.call('tk', 'windowingsystem')
            except:
                winsys = None
        if winsys is None:
            try:
                import tkinter as _tk
                root = _tk._get_default_root()
                if root is not None:
                    winsys = root.tk.call('tk', 'windowingsystem')
            except:
                winsys = None

        backend_cls = _NativeContextMenu if winsys == 'aqua' else _ToplevelContextMenu
        self._impl = backend_cls(
            master=master,
            minwidth=minwidth,
            width=width,
            minheight=minheight,
            height=height,
            target=target,
            anchor=anchor,
            attach=attach,
            offset=offset,
            hide_on_outside_click=hide_on_outside_click,
            items=items,
            density=density,
            command=command,
        )

        # Auto-bind the activation gesture to the target widget. Skip when
        # there's no target (no widget to bind on) or the caller explicitly
        # opted out so existing widgets that manage their own triggers
        # (OptionMenu, DropdownButton, Tableview, SideNav) keep working.
        if target is not None and trigger not in (None, 'manual', 'none'):
            self._bind_trigger(target, trigger)

    def _bind_trigger(self, target: Misc, trigger: str) -> None:
        """Bind `target`'s activation event to show this menu at the click."""
        from bootstack._runtime.utility import bind_right_click

        def show_at(event):
            self.show(position=(event.x_root, event.y_root))

        normalized = trigger.lower().replace('_', '-')
        if normalized in ('right-click', 'right'):
            bind_right_click(target, show_at)
        elif normalized in ('click', 'left-click', 'left'):
            target.bind('<Button-1>', show_at, add='+')
        elif normalized in ('double-click', 'double'):
            target.bind('<Double-Button-1>', show_at, add='+')
        elif normalized in ('shift-click', 'shift'):
            target.bind('<Shift-Button-1>', show_at, add='+')
        elif normalized in ('ctrl-click', 'control-click', 'ctrl', 'control'):
            target.bind('<Control-Button-1>', show_at, add='+')
        else:
            raise ValueError(
                f"Unknown trigger {trigger!r}. Use 'right-click', 'click', "
                f"'double-click', 'shift-click', 'ctrl-click', or 'manual'."
            )

    # ── Public API stubs ──────────────────────────────────────────────────────
    # Explicit method definitions so griffe and IDEs can see the API.
    # Each delegates to self._impl; on macOS the native backend returns key
    # strings instead of widget objects, so add_* return types are Any.

    def add_command(
            self,
            text: str = None,
            icon: str = None,
            command: Callable = None,
            disabled: bool = False,
            shortcut: str = None,
            key: str = None,
    ) -> ContextMenuItemResult:
        """Add a command item to the menu.

        Args:
            text: Item label text.
            icon: Icon name. Defaults to a blank placeholder to preserve alignment.
            command: Callable invoked when the item is clicked.
            disabled: If True the item is rendered disabled and cannot be clicked.
            shortcut: Keyboard shortcut label, either a registered shortcut key
                or a literal display string (e.g. `'Ctrl+S'`).
            key: Unique identifier. Auto-generated if not provided.
        """
        return self._impl.add_command(
            text=text, icon=icon, command=command,
            disabled=disabled, shortcut=shortcut, key=key,
        )

    def add_checkbutton(
            self,
            text: str = None,
            value: bool = False,
            command: Callable = None,
            key: str = None,
    ) -> ContextMenuItemResult:
        """Add a checkbutton item to the menu.

        Args:
            text: Item label text.
            value: Initial checked state.
            command: Callable invoked when the item is toggled.
            key: Unique identifier. Auto-generated if not provided.
        """
        return self._impl.add_checkbutton(text=text, value=value, command=command, key=key)

    def add_radiobutton(
            self,
            text: str = None,
            value: Any = None,
            variable: Any = None,
            command: Callable = None,
            key: str = None,
    ) -> ContextMenuItemResult:
        """Add a radiobutton item to the menu.

        Args:
            text: Item label text.
            value: Value assigned to `variable` when this item is selected.
            variable: Tkinter Variable shared across the radio group.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            command: Callable invoked when the item is selected.
            key: Unique identifier. Auto-generated if not provided.
        """
        return self._impl.add_radiobutton(
            text=text, value=value, variable=variable, command=command, key=key,
        )

    def add_separator(self, key: str = None) -> ContextMenuItemResult:
        """Add a horizontal separator to the menu.

        Args:
            key: Unique identifier. Auto-generated if not provided.
        """
        return self._impl.add_separator(key=key)

    def add_item(self, type: str, **kwargs: Any) -> ContextMenuItemResult:
        """Add a menu item by type name.

        Args:
            type: One of `'command'`, `'checkbutton'`, `'radiobutton'`,
                or `'separator'`.
            **kwargs: Forwarded to the matching `add_*` method.
        """
        return self._impl.add_item(type, **kwargs)

    def add_items(self, items: list[ContextMenuItem]) -> None:
        """Add multiple items at once.

        Args:
            items: List of `ContextMenuItem` objects or dicts with
                a `type` key and item kwargs.
        """
        self._impl.add_items(items)

    def insert_item(self, index: int, type: str, **kwargs: Any) -> ContextMenuItemResult:
        """Insert a new item at the given index.

        Args:
            index: Position to insert at (0-based).
            type: Item type — same values as `add_item`.
            **kwargs: Forwarded to the matching `add_*` method.
        """
        return self._impl.insert_item(index, type, **kwargs)

    def item(self, key_or_index: str | int) -> ContextMenuItemResult:
        """Return the item widget (or spec dict on macOS) for a key or index.

        Args:
            key_or_index: String key or integer index of the item.
        """
        return self._impl.item(key_or_index)

    def remove_item(self, key_or_index: str | int) -> None:
        """Remove and destroy the item at the given key or index.

        Args:
            key_or_index: String key or integer index of the item.
        """
        self._impl.remove_item(key_or_index)

    def move_item(self, from_key_or_index: str | int, to_index: int) -> ContextMenuItemResult:
        """Reorder an item to a new position.

        Args:
            from_key_or_index: Current key or index of the item.
            to_index: Target index.
        """
        return self._impl.move_item(from_key_or_index, to_index)

    def configure_item(
            self,
            key_or_index: str | int,
            option: str | None = None,
            **kwargs: Any,
    ) -> Any:
        """Get or set options on an individual menu item.

        Args:
            key_or_index: Key or index of the item.
            option: If provided without `kwargs`, returns the current value of
                this option. If omitted, returns the full option map.
            **kwargs: Option values to set.
        """
        return self._impl.configure_item(key_or_index, option, **kwargs)

    def show(self, position: tuple[int, int] = None) -> None:
        """Show the context menu.

        Args:
            position: Optional `(x, y)` screen coordinates. If omitted the
                menu is positioned relative to its target widget.
        """
        self._impl.show(position=position)

    def hide(self) -> None:
        """Hide the context menu."""
        self._impl.hide()

    def destroy(self) -> None:
        """Destroy the context menu and release all resources."""
        self._impl.destroy()

    def items(self, value: list[ContextMenuItem] = None) -> list[ContextMenuItemResult] | None:
        """Get or set the full item list.

        Args:
            value: If provided, replaces all current items. If omitted,
                returns the current item list.
        """
        return self._impl.items(value)

    def keys(self) -> tuple[str, ...]:
        """Return all item keys in insertion order."""
        return self._impl.keys()

    # Forward every other attribute (methods, configure delegates, etc.)
    # to the active backend. `_impl` itself is a real instance attribute
    # so it's resolved by normal attribute lookup before __getattr__ runs.
    def __getattr__(self, name: str):
        # __getattr__ is only consulted when normal lookup fails, so we
        # won't recurse on '_impl' here unless backend init raised.
        impl = self.__dict__.get('_impl')
        if impl is None:
            raise AttributeError(name)
        return getattr(impl, name)

    def __getitem__(self, key):
        return self._impl[key]

    def __setitem__(self, key, value):
        self._impl[key] = value