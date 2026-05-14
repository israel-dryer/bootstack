from __future__ import annotations

from typing import Any, Callable, Literal, TYPE_CHECKING, TypedDict

from typing_extensions import Unpack

from bootstack.widgets.composites.contextmenu import ContextMenu, ContextMenuItem
from bootstack.widgets.primitives.menubutton import MenuButton
from bootstack.widgets.mixins import configure_delegate
from bootstack.widgets.types import Master

if TYPE_CHECKING:
    from bootstack.core.signals import Signal


class DropdownButtonKwargs(TypedDict, total=False):
    image: Any
    icon: Any
    icon_only: bool
    compound: Literal['text', 'image', 'top', 'bottom', 'left', 'right', 'center', 'none'] | str
    padding: Any
    width: int
    underline: int
    state: Literal['normal', 'active', 'disabled', 'readonly'] | str
    takefocus: Any
    style: str
    class_: str
    cursor: str
    default: Any
    name: str
    textvariable: Any
    textsignal: Signal[str]
    accent: str
    density: Literal['default', 'compact']
    variant: str
    surface: str
    style_options: dict[str, Any]
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
            icon: Bootstyle icon spec for the button content.
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

        # passthrough methods
        self.add_radiobutton = self._context_menu.add_radiobutton
        self.add_command = self._context_menu.add_command
        self.add_checkbutton = self._context_menu.add_checkbutton
        self.add_separator = self._context_menu.add_separator
        self.add_item = self._context_menu.add_item
        self.add_items = self._context_menu.add_items
        self.insert_item = self._context_menu.insert_item
        self.remove_item = self._context_menu.remove_item
        self.move_item = self._context_menu.move_item
        self.configure_item = self._context_menu.configure_item
        self.items = self._context_menu.items

    def _build_context_menu(self):
        """Construct the ContextMenu with current items and options."""
        # Offset compensates for the focus-ring affordance baked into the
        # button image so the dropdown's left edge aligns with the visible
        # button border. Same treatment as OptionMenu.
        from bootstack.style.bootstyle_builder_base import BootstyleBuilderBase
        offset_x = BootstyleBuilderBase.scale_from_source(10)
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

