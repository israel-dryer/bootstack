from __future__ import annotations

from typing import Any, Callable

from bootstack.widgets.composites.dropdownbutton import DropdownButton as _InternalDropdownButton
from bootstack.widgets.public.base import PublicWidgetBase


class MenuButton(PublicWidgetBase):
    """A button that opens a dropdown menu when clicked.

    Items are added at construction via `items=` or dynamically with
    `add_item()`. The `on_select` callback fires for every item click,
    receiving a dict with `type`, `text`, and `value` keys.

    Args:
        label: Button label text.
        items: Initial list of `ContextMenuItem` dicts.
        on_select: Callback fired when any menu item is activated.
        icon: Icon shown on the button.
        icon_only: If True, hides the label (icon only).
        show_arrow: If True (default), shows the dropdown chevron.
        menu_options: Extra kwargs forwarded to the underlying `ContextMenu`
            (e.g. `{'anchor': 'se', 'offset': 4}`).
        disabled: If True, button is non-interactive.
        accent: Accent token, e.g. `'primary'`, `'danger'`.
        variant: Style variant, e.g. `'outline'`, `'ghost'`.
        density: Widget density — `'default'` or `'compact'`.
        parent: Override the context-stack parent.
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
        accent: str | None = None,
        variant: str | None = None,
        density: str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

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
        internal_kwargs.update(kwargs)

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
            shortcut: Keyboard shortcut hint displayed on the right.
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
        on_click: Callable[[], Any] | None = None,
        key: str | None = None,
    ) -> str:
        """Add a radio-button item to the dropdown.

        Args:
            label: Item label text.
            value: Value associated with this radio item.
            on_click: Callback fired on selection.
            key: Unique string key. Auto-generated if omitted.

        Returns:
            The key assigned to this item.
        """
        kw: dict[str, Any] = {"text": label}
        if value is not None:
            kw["value"] = value
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

    def update_item(self, key: str, **kwargs: Any) -> None:
        """Reconfigure a dropdown item after creation.

        Args:
            key: Key returned by an `add_*` method.
            **kwargs: Options forwarded to the item's configure method.
        """
        self._internal.configure_item(key, **kwargs)

    def remove_item(self, key: str) -> None:
        """Remove a dropdown item by key.

        Args:
            key: Key returned by an `add_*` method.
        """
        self._internal.remove_item(key)

    def show_menu(self) -> None:
        """Open the dropdown menu programmatically."""
        self._internal.show_menu()

    # ----- Properties -----

    def item(self, key: str) -> Any:
        """Return the item object for `key`.

        Args:
            key: Key returned by an `add_*` method.
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
        """The underlying `ContextMenu` — for advanced programmatic access."""
        return self._internal.context_menu

    @property
    def disabled(self) -> bool:
        return str(self._internal.cget("state")) == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")
