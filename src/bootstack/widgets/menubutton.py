from __future__ import annotations

from typing import Any, Callable

from bootstack.widgets._impl.composites.dropdownbutton import DropdownButton as _InternalDropdownButton
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets.types import AccentToken, VariantToken, WidgetDensity

# Public item type names → internal ContextMenu type strings.
_ITEM_TYPE_MAP: dict[str, str] = {
    "command":     "command",
    "check":       "checkbutton",
    "radio":       "radiobutton",
    "separator":   "separator",
    # accept legacy names so existing code doesn't break
    "checkbutton": "checkbutton",
    "radiobutton": "radiobutton",
}


def _resolve_item_type(type_: str) -> str:
    resolved = _ITEM_TYPE_MAP.get(type_)
    if resolved is None:
        raise ValueError(
            f"Unknown item type {type_!r}. "
            f"Use 'command', 'check', 'radio', or 'separator'."
        )
    return resolved


# Keys that map to explicit constructor parameters — user **kwargs must not
# override these silently.
_RESERVED_INTERNAL_KEYS = frozenset({
    "show_dropdown_button", "popdown_options", "text", "items", "command",
    "icon", "icon_only", "state", "accent", "variant", "density",
})


class MenuButton(PublicWidgetBase):
    """A button that opens a dropdown menu when clicked.

    Items are added at construction via ``items=`` or dynamically with
    ``add_item()``. The ``on_select`` callback fires for every item click,
    receiving a dict with ``type``, ``text``, and ``value`` keys.

    Args:
        label: Button label text. Defaults to an empty string.
        items: Initial list of item dicts. Each dict must have a ``type``
            key (``'command'``, ``'check'``, ``'radio'``, or
            ``'separator'``) plus item-specific keys.
        on_select: Callback fired when any menu item is activated. Receives
            a dict with ``type`` (str), ``text`` (str), and ``value`` (Any).
        icon: Icon name shown on the button face.
        icon_only: If ``True``, hides the label and shows only the icon.
            Inferred automatically when ``icon=`` is set and ``label`` is
            empty. Defaults to ``False``.
        show_arrow: If ``True`` (default), shows the dropdown chevron arrow.
            Pass ``False`` to hide it (useful when the icon implies the action).
        menu_options: Extra options forwarded to the underlying ``ContextMenu``
            at construction (e.g. ``{'anchor': 'se', 'offset': 4}``).
        disabled: If ``True``, button is shown but non-interactive. Defaults
            to ``False``.
        accent: Color intent token. One of ``'primary'``, ``'secondary'``,
            ``'info'``, ``'success'``, ``'warning'``, ``'danger'``,
            ``'default'``. Defaults to the theme default.
        variant: Style variant. One of ``'solid'``, ``'outline'``,
            ``'ghost'``. Defaults to ``'ghost'``.
        density: Layout density. ``'default'`` uses standard padding;
            ``'compact'`` reduces padding and button height.
        textsignal: ``Signal[str]`` bound to the button label text.
        parent: Override the context-stack parent widget.
    """

    def __init__(
        self,
        label: str = "",
        *,
        items: list[Any] | None = None,
        on_select: Callable[[dict[str, Any]], Any] | None = None,
        icon: str | None = None,
        icon_only: bool = False,
        show_arrow: bool = True,
        menu_options: dict[str, Any] | None = None,
        disabled: bool = False,
        accent: AccentToken | None = None,
        variant: VariantToken | None = None,
        density: WidgetDensity | None = None,
        textsignal: Any = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        # Build internal kwargs from explicit params first, then let **kwargs
        # add extras — but never let **kwargs clobber an explicitly-set key.
        internal_kwargs: dict[str, Any] = {
            "show_dropdown_button": show_arrow,
        }
        if menu_options is not None:
            internal_kwargs["popdown_options"] = menu_options
        if label:
            internal_kwargs["text"] = label
        if items is not None:
            internal_kwargs["items"] = items
        if on_select is not None:
            internal_kwargs["command"] = on_select
        if icon is not None:
            internal_kwargs["icon"] = icon
        if icon_only:
            internal_kwargs["icon_only"] = True
        if disabled:
            internal_kwargs["state"] = "disabled"
        if accent is not None:
            internal_kwargs["accent"] = accent
        if variant is not None:
            internal_kwargs["variant"] = variant
        if density is not None:
            internal_kwargs["density"] = density
        if textsignal is not None:
            internal_kwargs["textsignal"] = textsignal

        # Merge extra kwargs, skipping any that would override an explicit param.
        for k, v in kwargs.items():
            if k not in _RESERVED_INTERNAL_KEYS:
                internal_kwargs[k] = v

        self._internal = _InternalDropdownButton(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Item management -----

    def add_item(
        self,
        label: str,
        *,
        on_click: Callable[[], Any] | None = None,
        icon: str | None = None,
        shortcut: str | None = None,
        disabled: bool = False,
        key: str | None = None,
    ) -> str:
        """Add a command item to the dropdown.

        Args:
            label: Item label text.
            on_click: Callback fired when the item is clicked.
            icon: Icon name shown beside the label.
            shortcut: Keyboard shortcut hint displayed on the right. Accepts a
                modifier pattern (``"Mod+S"`` → ``"Ctrl+S"`` / ``"⌘S"``), a
                registered shortcut key name, or a literal display string.
            disabled: If True, item is shown but non-interactive.
            key: Unique string key. Auto-generated if omitted.

        Returns:
            The key assigned to this item.
        """
        kw: dict[str, Any] = {"text": label, "disabled": disabled}
        if on_click is not None:
            kw["command"] = on_click
        if icon is not None:
            kw["icon"] = icon
        if shortcut is not None:
            kw["shortcut"] = shortcut
        if key is not None:
            kw["key"] = key
        result = self._internal.add_command(**kw)
        return result.key if hasattr(result, "key") else key or label

    def add_check_item(
        self,
        label: str,
        *,
        value: bool = False,
        on_click: Callable[[], Any] | None = None,
        key: str | None = None,
    ) -> str:
        """Add a checkbutton item to the dropdown.

        Args:
            label: Item label text.
            value: Initial checked state.
            on_click: Callback fired on toggle.
            key: Unique string key. Auto-generated if omitted.

        Returns:
            The key assigned to this item.
        """
        kw: dict[str, Any] = {"text": label, "value": value}
        if on_click is not None:
            kw["command"] = on_click
        if key is not None:
            kw["key"] = key
        result = self._internal.add_checkbutton(**kw)
        return result.key if hasattr(result, "key") else key or label

    def add_radio_item(
        self,
        label: str,
        *,
        value: Any = None,
        selected: bool = False,
        on_click: Callable[[], Any] | None = None,
        key: str | None = None,
    ) -> str:
        """Add a radio-button item to the dropdown.

        All radio items in a ``MenuButton`` share one group variable
        automatically. Pass ``selected=True`` on the item that should be
        pre-selected on first open.

        Note:
            Values are stored as strings internally. Pass string values
            (e.g. ``value="100%"``) for predictable comparisons when reading
            the group selection via ``menu``.

        Args:
            label: Item label text.
            value: Value associated with this radio item. Stored as a string
                internally; defaults to ``label`` when omitted.
            selected: If ``True``, this item is the initial selection.
                Defaults to ``False``.
            on_click: Callback fired on selection.
            key: Unique string key. Auto-generated if omitted.

        Returns:
            The key assigned to this item.
        """
        from tkinter import StringVar
        if not hasattr(self, "_radio_variable"):
            self._radio_variable = StringVar(master=self._internal)
        str_value = str(value) if value is not None else label
        if selected:
            self._radio_variable.set(str_value)
        kw: dict[str, Any] = {
            "text": label,
            "value": str_value,
            "variable": self._radio_variable,
        }
        if on_click is not None:
            kw["command"] = on_click
        if key is not None:
            kw["key"] = key
        result = self._internal.add_radiobutton(**kw)
        return result.key if hasattr(result, "key") else key or label

    def add_separator(self, *, key: str | None = None) -> None:
        """Add a horizontal separator to the dropdown."""
        kw: dict[str, Any] = {}
        if key is not None:
            kw["key"] = key
        self._internal.add_separator(**kw)

    def add_items(self, items: list[Any]) -> None:
        """Add multiple items at once from a list of item dicts.

        Each dict must have a ``type`` key plus item-specific keys:

        .. code-block:: python

           mb.add_items([
               {"type": "command",   "text": "Edit",   "icon": "pencil"},
               {"type": "command",   "text": "Delete", "icon": "trash"},
               {"type": "separator"},
               {"type": "check",     "text": "Pinned", "value": True},
               {"type": "radio",     "text": "Small",  "value": "sm"},
           ])

        Args:
            items: List of item dicts. ``type`` accepts ``'command'``,
                ``'check'``, ``'radio'``, or ``'separator'``.
        """
        translated = []
        for item in items:
            item = dict(item)
            if "type" in item:
                item["type"] = _resolve_item_type(item["type"])
            translated.append(item)
        self._internal.add_items(translated)

    def insert_item(self, index: int, type: str, **kwargs: Any) -> str:
        """Insert a new item at a specific position.

        Args:
            index: Zero-based position to insert at.
            type: Item type — ``'command'``, ``'check'``, ``'radio'``,
                or ``'separator'``.
            **kwargs: Forwarded to the matching ``add_*`` method.

        Returns:
            The key assigned to the new item.
        """
        result = self._internal.insert_item(index, _resolve_item_type(type), **kwargs)
        return result.key if hasattr(result, "key") else result

    def move_item(self, key: str, to_index: int) -> None:
        """Move an existing item to a new position.

        Args:
            key: Key of the item to move.
            to_index: Target zero-based index.
        """
        self._internal.move_item(key, to_index)

    def update_item(self, key: str, **kwargs: Any) -> None:
        """Reconfigure a dropdown item after creation.

        Args:
            key: Key returned by an ``add_*`` method.
            **kwargs: Options forwarded to the item's configure method.
        """
        self._internal.configure_item(key, **kwargs)

    def remove_item(self, key: str) -> None:
        """Remove a dropdown item by key.

        Args:
            key: Key returned by an ``add_*`` method.
        """
        self._internal.remove_item(key)

    def show_menu(self) -> None:
        """Open the dropdown menu programmatically.

        Has no effect if the button is disabled or read-only.
        """
        if not self._internal.instate(("!disabled", "!readonly")):
            return
        self._internal.show_menu()

    # ----- Properties -----

    def item(self, key: str) -> Any:
        """Return the item object for ``key``.

        Args:
            key: Key returned by an ``add_*`` method.
        """
        return self._internal.context_menu.item(key)

    @property
    def items(self) -> list[Any]:
        """All menu items in insertion order."""
        return self._internal.items() or []

    @property
    def keys(self) -> tuple[str, ...]:
        """Keys of all menu items in insertion order."""
        return self._internal.keys()

    @property
    def menu(self) -> Any:
        """The underlying ``ContextMenu`` — for advanced programmatic access."""
        return self._internal.context_menu

    @property
    def disabled(self) -> bool:
        """Whether the button is non-interactive."""
        return self._internal.instate(("disabled",))

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")
