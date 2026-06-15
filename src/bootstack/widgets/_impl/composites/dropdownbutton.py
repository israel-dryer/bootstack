from __future__ import annotations

from typing import Any, Callable, TYPE_CHECKING

from typing_extensions import Unpack

from bootstack.widgets._impl.composites.contextmenu import ContextMenu, ContextMenuItem, ContextMenuItemResult
from bootstack.widgets._impl.primitives._menubutton import MenuButton
from bootstack.widgets._impl.mixins import configure_delegate
from bootstack.widgets.types import Master, StyledKwargs, CompoundMode, WidgetState, WidgetDensity

if TYPE_CHECKING:
    from bootstack.signals import Signal


class DropdownButtonKwargs(StyledKwargs, total=False):
    image: Any
    icon: Any
    icon_only: bool
    compound: CompoundMode
    padding: Any
    width: int
    underline: int
    state: WidgetState
    default: Any
    textvariable: Any
    textsignal: Signal[str]
    density: WidgetDensity
    popdown_options: dict[str, Any]
    show_dropdown_button: bool
    dropdown_button_icon: str | dict


class DropdownButton(MenuButton):
    """A button that opens a ContextMenu dropdown when clicked.

    DropdownButton combines a MenuButton with a ContextMenu, adding a chevron
    indicator and optional item-click callbacks. Items can be added at
    construction or dynamically via `add_command`, `add_checkbutton`,
    `add_radiobutton`, and `add_separator`.
    """

    def __init__(
            self,
            master: Master = None,
            text: Any = None,
            items: list[ContextMenuItem] = None,
            command: Callable = None,
            **kwargs: Unpack[DropdownButtonKwargs],
    ):
        """Create a dropdown button backed by a ContextMenu.

        Args:
            master: Parent widget. If None, uses the default root window.
            text: Label text for the button.
            items: Initial list of ContextMenuItem entries.
            command: Callback invoked when any menu item is clicked. Receives a
                dict with keys `type` (str), `text` (str), and `value` (Any).
                Use `configure(command=...)` to change or clear after construction.

        Other Parameters:
            image: Tk image to display.
            icon: StyleResolver icon spec for the button content.
            icon_only: Whether to reserve label padding when showing only an icon.
            compound: Placement of image relative to text.
            padding: Extra padding around the button content.
            density: Widget density — 'default' or 'compact'.
            width: Width of the button.
            underline: Index of underlined character in text.
            state: Widget state — 'normal', 'active', 'disabled', or 'readonly'.
            takefocus: Participation in focus traversal.
            style: Explicit ttk style name.
            textvariable: Existing Tk variable for the label text.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            textsignal: Signal bound to the textvariable.
            accent: Accent token for styling (e.g., 'primary', 'danger').
            variant: Style variant (e.g., 'outline', 'ghost').
            surface: Surface token for style.
            style_options: Dict forwarded to the menubutton style builder.
            popdown_options: Dict forwarded to ContextMenu (e.g., anchor, attach, offset).
            show_dropdown_button: Show/hide the chevron.
            dropdown_button_icon: Icon name for the chevron.
        """
        style_options = kwargs.pop('style_options', {})
        style_options.update(
            self._capture_style_options(
                options=['icon', 'icon_only', 'density', 'show_dropdown_button', 'dropdown_button_icon'],
                source=kwargs
            )
        )
        # Infer icon_only when an icon is set but no text label is provided.
        if 'icon_only' not in style_options and style_options.get('icon') and not text:
            style_options['icon_only'] = True
        kwargs['style_options'] = style_options
        self._items = items if items else []
        self._command = command
        self._popdown_options = kwargs.pop('popdown_options', {})

        # Store the textvariable if provided, or create a new one
        super().__init__(master, text=text, **kwargs)

        # Create menu items that update the shared variable
        self._context_menu = self._build_context_menu()

        # Bind menu display to button events
        self.bind('<Button-1>', lambda _: self.show_menu(), add="+")
        self.bind('<Return>', lambda _: self.show_menu(), add="+")
        self.bind('<KP_Enter>', lambda _: self.show_menu(), add="+")


    def _build_context_menu(self):
        """Construct the ContextMenu with current items and options."""
        # Offset compensates for the focus-ring affordance baked into the
        # button image so the dropdown's left edge aligns with the visible
        # button border. Same treatment as OptionMenu.
        from bootstack.style.style_builder_base import StyleBuilderBase
        offset_x = StyleBuilderBase.scale_from_source(10)
        density = self.configure_style_options('density') or 'default'
        options = {
            "anchor": "nw",
            "attach": "sw",
            "offset": (offset_x, 0),
            "density": density,
        }
        options.update(self._popdown_options)
        # DropdownButton manages its own activation (left-click, Return/
        # KP_Enter via show_menu), so opt out of ContextMenu's auto-trigger.
        cm = ContextMenu(self, target=self, items=self._items, trigger=None, command=self._command, **options)
        return cm

    @property
    def context_menu(self):
        """Returns the context menu widget"""
        return self._context_menu

    def show_menu(self):
        """Show the dropdown menu unless disabled or readonly."""
        if not self.instate(("!disabled", "!readonly")):
            return
        self._context_menu.show()

    def add_command(
            self,
            text: str = None,
            icon: str = None,
            command: Callable = None,
            disabled: bool = False,
            shortcut: str = None,
            key: str = None,
    ) -> ContextMenuItemResult:
        """Add a command item to the dropdown menu.

        Args:
            text: Item label text.
            icon: Icon name. Defaults to a blank placeholder to preserve alignment.
            command: Callable invoked when the item is clicked.
            disabled: If True the item is rendered disabled and cannot be clicked.
            shortcut: Keyboard shortcut label, either a registered shortcut key
                or a literal display string (e.g. `'Ctrl+S'`).
            key: Unique identifier. Auto-generated if not provided.
        """
        return self._context_menu.add_command(
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
        """Add a checkbutton item to the dropdown menu.

        Args:
            text: Item label text.
            value: Initial checked state.
            command: Callable invoked when the item is toggled.
            key: Unique identifier. Auto-generated if not provided.
        """
        return self._context_menu.add_checkbutton(
            text=text, value=value, command=command, key=key,
        )

    def add_radiobutton(
            self,
            text: str = None,
            value: Any = None,
            variable: Any = None,
            command: Callable = None,
            key: str = None,
    ) -> ContextMenuItemResult:
        """Add a radiobutton item to the dropdown menu.

        Args:
            text: Item label text.
            value: Value assigned to `variable` when this item is selected.
            variable: Tkinter Variable shared across the radio group.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            command: Callable invoked when the item is selected.
            key: Unique identifier. Auto-generated if not provided.
        """
        return self._context_menu.add_radiobutton(
            text=text, value=value, variable=variable, command=command, key=key,
        )

    def add_separator(self, key: str = None) -> ContextMenuItemResult:
        """Add a horizontal separator to the dropdown menu.

        Args:
            key: Unique identifier. Auto-generated if not provided.
        """
        return self._context_menu.add_separator(key=key)

    def add_item(self, type: str, **kwargs: Any) -> ContextMenuItemResult:
        """Add a menu item by type name.

        Args:
            type: One of `'command'`, `'checkbutton'`, `'radiobutton'`,
                or `'separator'`.
            **kwargs: Forwarded to the matching `add_*` method.
        """
        return self._context_menu.add_item(type, **kwargs)

    def add_items(self, items: list[ContextMenuItem]) -> None:
        """Add multiple items at once.

        Args:
            items: List of `ContextMenuItem` objects or dicts with
                a `type` key and item kwargs.
        """
        self._context_menu.add_items(items)

    def insert_item(self, index: int, type: str, **kwargs: Any) -> ContextMenuItemResult:
        """Insert a new item at the given index.

        Args:
            index: Position to insert at (0-based).
            type: Item type — same values as `add_item`.
            **kwargs: Forwarded to the matching `add_*` method.
        """
        return self._context_menu.insert_item(index, type, **kwargs)

    def remove_item(self, key_or_index: str | int) -> None:
        """Remove and destroy the item at the given key or index.

        Args:
            key_or_index: String key or integer index of the item.
        """
        self._context_menu.remove_item(key_or_index)

    def move_item(self, from_key_or_index: str | int, to_index: int) -> ContextMenuItemResult:
        """Reorder an item to a new position.

        Args:
            from_key_or_index: Current key or index of the item.
            to_index: Target index.
        """
        return self._context_menu.move_item(from_key_or_index, to_index)

    def configure_item(
            self,
            key_or_index: str | int,
            option: str | None = None,
            **kwargs: Any,
    ) -> Any:
        """Get or set options on an individual menu item.

        Args:
            key_or_index: Key or index of the item.
            option: If provided without `kwargs`, returns the current value
                of this option. If omitted, returns the full option map.
            **kwargs: Option values to set.
        """
        return self._context_menu.configure_item(key_or_index, option, **kwargs)

    def items(self, value: list[ContextMenuItem] = None) -> list[ContextMenuItemResult] | None:
        """Get or set the full item list.

        Args:
            value: If provided, replaces all current items. If omitted,
                returns the current item list.
        """
        return self._context_menu.items(value)

    def keys(self) -> tuple[str, ...]:
        """Return all item keys in insertion order."""
        return self._context_menu.keys()

    @configure_delegate('command')
    def _delegate_command(self, value=None):
        """Get or set the item-click callback."""
        if value is None and not self._command:
            return self._command
        self._command = value
        self._context_menu.configure(command=value)
        return None

    @configure_delegate('popdown_options')
    def _delegate_popdown_options(self, value=None):
        """Get or set ContextMenu positioning options (anchor, attach, offset, etc.)."""
        if value is None:
            return self._popdown_options
        else:
            self._popdown_options = value
            return self.context_menu.configure(**value)

    @configure_delegate('show_dropdown_button')
    def _delegate_show_dropdown_button(self, value=None):
        """Get or set visibility of the dropdown chevron."""
        if value is None:
            return self.configure_style_options('show_dropdown_button')
        else:
            self.configure_style_options(show_dropdown_button=value)
            return self.rebuild_style()

    @configure_delegate('dropdown_button_icon')
    def _delegate_dropdown_button_icon(self, value=None):
        """Get or set the dropdown chevron icon name."""
        if value is None:
            return self.configure_style_options('dropdown_button_icon')
        else:
            self.configure_style_options(dropdown_button_icon=value)
            return self.rebuild_style()
