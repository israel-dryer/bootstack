from __future__ import annotations

from tkinter import StringVar
from typing import Any, Callable, TypedDict, TYPE_CHECKING

from typing_extensions import Unpack

from bootstack.events import ChangeEvent
from bootstack.widgets._core.options import normalize_options, option_display, record_to_dict
from bootstack.widgets._impl.composites.contextmenu import ContextMenu, ContextMenuItem
from bootstack.widgets._impl.primitives._menubutton import MenuButton
from bootstack.widgets._impl.mixins import configure_delegate
from bootstack.widgets.types import Master, StyledKwargs, CompoundMode, WidgetState, Option

if TYPE_CHECKING:
    from bootstack.signals import Signal


class OptionMenuKwargs(StyledKwargs, total=False):
    command: Callable[[], Any] | None
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
    localize: Any
    show_dropdown_button: bool
    dropdown_button_icon: str | dict


class OptionMenu(MenuButton):
    """A single-selection dropdown menu backed by a ContextMenu.

    Renders as a `MenuButton` with a chevron icon. Clicking the button opens
    a popup menu containing the provided options as radiobutton items. Selecting
    an item updates the displayed text and fires a `<<Change>>` event.

    """

    def __init__(
            self,
            master: Master = None,
            value: Any = None,
            options: list[Option] = None,
            **kwargs: Unpack[OptionMenuKwargs],
    ):
        """Create an OptionMenu backed by a ContextMenu.

        Args:
            master: Parent widget. If None, uses the default root window.
            value: Initial selected value (value-space). Must match one of the
                options unless it is None/empty.
            options: Options to populate the menu — each a string,
                `(text, value)` tuple, or `{'text', 'value'}` dict. The menu
                shows each option's text; selecting one emits its value.

        Other Parameters:
            command: Callback invoked when the value changes via menu selection.
            image: Tk image to display.
            icon: Bootstyle icon spec for the label content.
            icon_only: Whether to reserve label padding when showing only an icon.
            compound: Placement of image relative to text.
            padding: Extra padding around the menubutton content.
            width: Width of the menubutton.
            underline: Index of underlined character in text.
            state: Widget state ('normal', 'active', 'disabled', 'readonly').
            takefocus: Participation in focus traversal.
            style: Explicit ttk style name (overrides accent/variant).
            textvariable: Existing Tk variable to bind; new StringVar created if omitted.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            textsignal: Signal bound to the textvariable.
            accent: Accent token for styling, e.g. 'primary', 'danger', 'success'.
            variant: Style variant, e.g. 'solid', 'outline'.
            surface: Surface token for style.
            style_options: Dict forwarded to the style builder (e.g., icon_only, surface).
            show_dropdown_button: Toggle visibility of the dropdown chevron.
            dropdown_button_icon: Icon name for the chevron; defaults to 'caret-down-fill'.
        """
        style_options = kwargs.pop('style_options', {})
        style_options.update(
            self._capture_style_options(
                options=['icon_only', 'icon', 'show_dropdown_button', 'dropdown_button_icon'],
                source=kwargs
            )
        )

        self._bind_id = None
        # Localization mode for the option labels + button face. None defers to
        # the app's localize_mode; False keeps the raw labels untranslated.
        self._localize = kwargs.pop('localize', None)
        # Normalize options once; keep bidirectional text<->value maps so the
        # menu can display text while the public value stays in value-space.
        self._records = normalize_options(options)
        self._rebuild_option_maps()

        # Store the textvariable if provided, or create a new one. This variable
        # holds the raw VALUE-KEY text (untranslated): it drives the radio
        # highlight, the public value/selection, and <<Change>> in value-space.
        self._textvariable = kwargs.pop('textvariable', None)
        if self._textvariable is None:
            self._textvariable = StringVar(value=self._resolve_initial_text(value))

        # A separate variable backs the visible button face, holding the
        # (optionally translated) DISPLAY text — decoupled from the value key so
        # the face can localize while value-space stays raw.
        self._display_var = StringVar(value=self._display_text(self._textvariable.get()))

        # The mixin must not touch the face (we own its translation), so disable
        # its localization; OptionMenu localizes the face via `_display_var`.
        super().__init__(master, text=self._display_var.get(), localize=False, style_options=style_options, **kwargs)

        # Bind the textsignal to the value-key variable (drives <<Change>> + the
        # public signal), then point the visible face at the display variable.
        self.configure(textvariable=self._textvariable)
        self._ttk_base.configure(self, textvariable=self._display_var)

        # Bind signal to change event (also keeps the face display in sync)
        self._bind_id = self._bind_change_event()
        self._sync_display()
        # The locale-change event is generated on the root; bind there (not on
        # self) so the face re-translates live, matching the mixin's pattern.
        self.winfo_toplevel().bind('<<LocaleChanged>>', lambda _e: self._sync_display(), add="+")

        # Create menu items that update the shared variable
        self._context_menu = self._build_context_menu()

        # Bind menu display to button events
        self.bind('<Button-1>', lambda _: self.show_menu(), add="+")
        self.bind('<Return>', lambda _: self.show_menu(), add="+")
        self.bind('<KP_Enter>', lambda _: self.show_menu(), add="+")

    def _effective_localize(self) -> Any:
        """Resolve the active localize mode, deferring to the app when unset."""
        if self._localize is not None:
            return self._localize
        try:
            from bootstack._runtime.app import get_app_settings
            return get_app_settings().localize_mode
        except Exception:
            return 'auto'

    def _display_text(self, raw: str) -> str:
        """Map a raw value-key label to its display text under the active mode.

        Returns the label unchanged when localization is off or no translation
        is registered; otherwise the catalog translation.
        """
        if not raw:
            return ''
        if self._effective_localize() is False:
            return raw
        try:
            from bootstack.i18n import MessageCatalog
            return MessageCatalog.translate(raw) or raw
        except Exception:
            return raw

    def _sync_display(self) -> None:
        """Refresh the visible face from the current value-key text."""
        self._display_var.set(self._display_text(self._textvariable.get()))

    def _rebuild_option_maps(self) -> None:
        """Rebuild the text<->value lookups from the current records.

        Duplicate texts keep the first value; duplicate values keep the first
        text. A SelectButton uses a single shared variable keyed on text, so
        duplicate texts with distinct values cannot be told apart — keep option
        texts unique.
        """
        self._value_by_text: dict[str, Any] = {}
        self._text_by_value: dict[Any, str] = {}
        for rec in self._records:
            self._value_by_text.setdefault(rec.text, rec.value)
            try:
                self._text_by_value.setdefault(rec.value, rec.text)
            except TypeError:
                pass  # unhashable value — no reverse mapping; display still works

    def _resolve_initial_text(self, value: Any) -> str:
        """Map an initial value-space value to its display text.

        Returns the empty string for None/empty; raises if the value matches no
        option.
        """
        if value is None or value == "":
            return ""
        try:
            if value in self._text_by_value:
                return self._text_by_value[value]
        except TypeError:
            pass
        raise ValueError(f"{value!r} is not one of the options")

    def _bind_change_event(self):
        """(Re)bind textsignal to emit <<Change>> Tk events (in value-space).

        The same subscription keeps the localized face in sync, since the value
        key changes whenever a selection is made.
        """
        if self._bind_id is not None:
            self.textsignal.unsubscribe(self._bind_id)

        def _on_change(text: str) -> None:
            self._sync_display()
            self.event_generate(
                '<<Change>>',
                data=ChangeEvent(value=self._value_by_text.get(text, text) if text else None),
            )

        return self.textsignal.subscribe(_on_change)

    def _build_context_menu(self):
        # Affordance baked into the button image (focus ring + border line in
        # source-px); aligning the menu's left edge to it matches the visible
        # button border the same way the combobox popdown does.
        from bootstack.style.bootstyle_builder_base import BootstyleBuilderBase
        offset_x = BootstyleBuilderBase.scale_from_source(10)

        density = self.configure_style_options('density') or 'default'

        menu_items = []
        for rec in self._records:
            icon, disabled = option_display(rec)
            # A per-option localize key overrides the widget-level mode.
            item_localize = rec.extras.get("localize", self._localize)
            menu_items.append(
                ContextMenuItem(
                    type="radiobutton",
                    text=rec.text,
                    variable=self._textvariable,
                    value=rec.text,
                    icon=icon,
                    disabled=disabled,
                    localize=item_localize,
                )
            )
        return ContextMenu(
            self, target=self, items=menu_items,
            anchor="nw", attach="sw",
            offset=(offset_x, 0),
            density=density,
            # OptionMenu drives activation via `show_menu` (left-click,
            # Return/KP_Enter), not ContextMenu's auto-trigger.
            trigger=None,
        )

    def show_menu(self):
        """Show the dropdown menu unless disabled or readonly."""
        if not self.instate(("!disabled", "!readonly")):
            return
        # Match the menu's minimum width to the visible button width so the
        # dropdown never renders narrower than its trigger.
        from bootstack.style.bootstyle_builder_base import BootstyleBuilderBase
        affordance = BootstyleBuilderBase.scale_from_source(10)
        target_w = self.winfo_width() - 2 * affordance
        if target_w > 0:
            self._context_menu.configure(minwidth=max(150, target_w))
        self._context_menu.show()

    @property
    def text(self) -> str:
        """The display label currently shown on the button (translated)."""
        return self._display_var.get()

    @property
    def selection(self) -> dict | None:
        """The selected option as a full record dict (the data bag), or None."""
        text = self._textvariable.get()
        if text == "":
            return None
        for rec in self._records:
            if rec.text == text:
                return record_to_dict(rec)
        return None

    def get(self) -> Any:
        """Return the current value (value-space), or `None` if nothing is selected."""
        text = self._textvariable.get()
        if text == "":
            return None
        return self._value_by_text.get(text, text)

    def set(self, value: Any) -> None:
        """Select the option whose value is `value`, updating the displayed text.

        Passing None or `''` clears the selection. A value that matches no
        option raises `ValueError`.
        """
        if value is None or value == "":
            self._textvariable.set("")
            return
        try:
            text = self._text_by_value[value]
        except (KeyError, TypeError):
            raise ValueError(f"{value!r} is not one of the options")
        self._textvariable.set(text)

    @property
    def value(self) -> str:
        """Get or set the current value."""
        return self.get()

    @value.setter
    def value(self, value: Any) -> None:
        self.set(value)

    def on_changed(self, callback: Callable) -> str:
        """Register a callback for `<<Change>>` events.

        Args:
            callback: Called when a menu item is selected. Receives a Tk event
                object; `event.data` is a `ChangeEvent` with the attribute
                `value` (the newly selected value, coerced to string).

        Returns:
            Bind ID — pass to `off_changed()` to unsubscribe.
        """
        return self.bind('<<Change>>', callback, add="+")

    def off_changed(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<Change>>`.

        Args:
            bind_id: ID returned by `on_changed()`. If None, removes all.
        """
        self.unbind('<<Change>>', bind_id)

    @configure_delegate('options')
    def _delegate_options(self, value=None):
        """Get the normalized option records, or set new options."""
        if value is None:
            return list(self._records)
        else:
            self._records = normalize_options(value)
            self._rebuild_option_maps()
            # Reconcile the current selection: if its display text is no longer
            # one of the options, clear it so the button never shows a value the
            # list can't offer (and no menu item stays phantom-selected).
            if self._textvariable.get() not in self._value_by_text:
                self._textvariable.set("")
            if self._context_menu:
                self._context_menu.destroy()
            self._context_menu = self._build_context_menu()
        return None

    @configure_delegate('value')
    def _delegate_value(self, value):
        """Get or set the current value."""
        if value is None:
            return self.value
        else:
            self.value = value
        return None

    @configure_delegate('textsignal')
    def _delegate_textsignal(self, value=None):
        """Get or set the textsignal binding."""
        if value is None:
            return super()._delegate_textsignal()
        else:
            super()._delegate_textsignal(value)
            self._bind_change_event()
        return None

    @configure_delegate('show_dropdown_button')
    def _delegate_show_dropdown_button(self, value=None):
        """Get or set visibility of the dropdown chevron."""
        if value is None:
            return self.configure_style_options('show_dropdown_button')
        else:
            self.configure_style_options(show_dropdown_button=value)
            return self.rebuild_style()

    @configure_delegate('dropdown_button_icon')
    def _delegate_dropdown_button_icon(self, value):
        """Get or set the dropdown chevron icon name."""
        if value is None:
            return self.configure_style_options('dropdown_button_icon')
        else:
            self.configure_style_options(dropdown_button_icon=value)
            return self.rebuild_style()
