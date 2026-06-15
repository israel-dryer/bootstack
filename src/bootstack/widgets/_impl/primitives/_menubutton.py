from __future__ import annotations

from tkinter import ttk
from typing import Any, Literal, TYPE_CHECKING

from typing_extensions import Unpack

from bootstack._core.mixins.ttk_state import TtkStateMixin
from bootstack._core.mixins.widget import WidgetCapabilitiesMixin
from bootstack.widgets._impl._internal.wrapper_base import TTKWrapperBase
from bootstack.widgets._impl.mixins import IconMixin, LocalizationMixin, TextSignalMixin
from bootstack.widgets.types import Master, StyledKwargs, CompoundMode, WidgetState, WidgetDensity

if TYPE_CHECKING:
    from bootstack.signals import Signal


class MenuButtonKwargs(StyledKwargs, total=False):
    # Standard ttk.Menubutton options
    text: Any
    image: Any
    icon: Any
    icon_only: bool
    compound: CompoundMode
    direction: Any
    menu: Any
    padding: Any
    state: WidgetState
    textvariable: Any
    textsignal: Signal[Any]

    # bootstack-specific extensions
    density: WidgetDensity
    localize: bool | Literal['auto']


class MenuButton(LocalizationMixin, TextSignalMixin, IconMixin, TTKWrapperBase, WidgetCapabilitiesMixin, TtkStateMixin, ttk.Menubutton):
    """bootstack wrapper for `ttk.Menubutton` with themed styling and icon support."""

    _ttk_base = ttk.Menubutton

    def __init__(self, master: Master = None, **kwargs: Unpack[MenuButtonKwargs]) -> None:
        """Create a themed bootstack Menubutton.

        Args:
            master: Parent widget. If None, uses the default root window.

        Other Parameters:
            text: Text to display in the menubutton.
            image: Image to display.
            icon: Theme-aware icon spec handled by the style system.
            icon_only: If True, removes the additional padding reserved for label text.
            compound: Placement of the image relative to text.
            direction: Direction for the menu to appear.
            menu: Associated tk.Menu instance.
            padding: Extra space around the content.
            density: Widget density — 'default' or 'compact'.
            state: Widget state — 'normal', 'active', 'disabled', or 'readonly'.
            takefocus: Whether the widget participates in focus traversal.
            textvariable: Tk variable linked to the text.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            textsignal: Reactive Signal linked to the text (auto-synced with textvariable).
            style: Explicit ttk style name (overrides accent/variant).
            accent: Accent token for styling, e.g. 'primary', 'danger', 'success'.
            variant: Style variant, e.g. 'solid', 'outline', 'ghost'.
            surface: Optional surface token; otherwise inherited.
            style_options: Optional dict forwarded to the style builder.
            localize: Determines the widget's localization mode.
        """
        kwargs.update(style_options=self._capture_style_options(['icon_only', 'icon', 'density'], kwargs))
        super().__init__(master, **kwargs)

        # When a native tk.Menu is attached, post it ourselves with the
        # focus-ring affordance offset so it aligns with the visible button
        # border. Subclasses (OptionMenu, DropdownButton) use a ContextMenu
        # and override show_menu, so this only affects the native path.
        # On Aqua, Tk's native Menubutton class binding drives an NSMenu
        # state machine that manages mouse/focus capture; bypassing it with
        # a manual `menu post` strands focus after item selection, so we
        # skip the offset path on Mac and let the default class binding run.
        if self.tk.call('tk', 'windowingsystem') != 'aqua':
            self.bind("<Button-1>", self._on_button_press, add="+")

    def _on_button_press(self, _event):
        """Focus self, and if a native menu is attached, post it with offset."""
        self.focus_set()
        try:
            menu_path = self.cget('menu')
        except Exception:
            menu_path = None
        if not menu_path:
            return None
        try:
            # If the menu is already visible, unpost so a second click closes it.
            if int(self.tk.eval(f"winfo viewable {menu_path}")):
                self.tk.call(menu_path, 'unpost')
                return 'break'
            from bootstack.style.style_builder_base import StyleBuilderBase
            offset = StyleBuilderBase.scale_from_source(10)
            x = self.winfo_rootx() + offset
            y = self.winfo_rooty() + self.winfo_height()
            self.tk.call(menu_path, 'post', x, y)
        except Exception:
            return None
        # Suppress Tk's default class binding so it doesn't also post the
        # menu at its un-offset position.
        return 'break'
