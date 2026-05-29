from __future__ import annotations

from typing import Any, Callable

from bootstack.widgets._impl.composites.contextmenu import ContextMenu as _InternalContextMenu
from bootstack.widgets._impl.composites.contextmenu import ContextMenuItem

_TRIGGER_MAP: dict[str | None, str | None] = {
    "right_click": "right-click",
    "left_click": "left-click",
    "double_click": "double-click",
    None: None,
    "manual": None,
}


def _resolve_tk(widget: Any) -> Any:
    """Return the underlying Tk widget from a public wrapper or pass through."""
    return getattr(widget, "_internal", widget)


class ContextMenu:
    """A popup menu that attaches to a target widget.

    Items fire an `on_select` callback receiving a dict with `type`, `text`,
    and `value` keys.

    Args:
        target: Widget the menu attaches to. Accepts public widgets or raw Tk
            widgets. Defaults to the root window.
        min_width: Minimum menu width in pixels. Default `150`.
        trigger: Gesture that opens the menu — `'right_click'` (default),
            `'left_click'`, `'double_click'`, or `None` (manual only).
        on_select: Callback fired when any item is activated.
        items: Initial list of `ContextMenuItem` dicts to add at construction.
        density: Item density — `'default'` or `'compact'`.
        parent: Parent widget for Tk hierarchy. Defaults to `target`.
    """

    def __init__(
        self,
        target: Any = None,
        *,
        min_width: int = 150,
        trigger: str | None = "right_click",
        on_select: Callable[[dict[str, Any]], Any] | None = None,
        items: list[Any] | None = None,
        density: str = "default",
        parent: Any = None,
    ) -> None:
        tk_target = _resolve_tk(target) if target is not None else None
        tk_master = _resolve_tk(parent) if parent is not None else tk_target

        internal_kwargs: dict[str, Any] = {
            "minwidth": min_width,
            "trigger": _TRIGGER_MAP.get(trigger, trigger),
            "density": density,
        }
        if on_select is not None:
            internal_kwargs["command"] = on_select
        if items is not None:
            internal_kwargs["items"] = items
        if tk_target is not None:
            internal_kwargs["target"] = tk_target

        self._internal = _InternalContextMenu(tk_master, **internal_kwargs)

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
        """Add a command item.

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
        """Add a checkbutton item.

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
        variable: Any = None,
        on_click: Callable[[], Any] | None = None,
        key: str | None = None,
    ) -> str:
        """Add a radiobutton item.

        Args:
            label: Item label text.
            value: Value assigned when this item is selected.
            variable: Shared Tk variable for the radio group.
            on_click: Callback fired when selected.
            key: Unique string key. Auto-generated if omitted.

        Returns:
            The key assigned to this item.
        """
        kw: dict[str, Any] = {"text": label}
        if value is not None:
            kw["value"] = value
        if variable is not None:
            kw["variable"] = variable
        if on_click is not None:
            kw["command"] = on_click
        if key is not None:
            kw["key"] = key
        result = self._internal.add_radiobutton(**kw)
        return result.key if hasattr(result, "key") else key or label

    def add_separator(self, *, key: str | None = None) -> None:
        """Add a horizontal separator.

        Args:
            key: Unique string key. Auto-generated if omitted.
        """
        kw: dict[str, Any] = {}
        if key is not None:
            kw["key"] = key
        self._internal.add_separator(**kw)

    def update_item(self, key: str, **kwargs: Any) -> None:
        """Reconfigure an item after creation.

        Args:
            key: Key returned by `add_item()` / `add_check_item()` etc.
            **kwargs: Options forwarded to the item's configure method.
        """
        self._internal.configure_item(key, **kwargs)

    def remove_item(self, key: str) -> None:
        """Remove an item by key.

        Args:
            key: Key returned by an `add_*` method.
        """
        self._internal.remove_item(key)

    # ----- Properties -----

    @property
    def keys(self) -> tuple[str, ...]:
        """Keys of all items in insertion order."""
        return self._internal.keys()

    # ----- Display -----

    def show(self, position: tuple[int, int] | None = None) -> "ContextMenu":
        """Show the menu, optionally at a screen `(x, y)` position.

        Returns:
            `self` — allows chaining: `ContextMenu(target).add_item(...).show()`.
        """
        self._internal.show(position)
        return self

    def hide(self) -> None:
        """Hide the menu."""
        self._internal.hide()