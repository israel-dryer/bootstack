from __future__ import annotations

from typing import Any, Callable

from bootstack.widgets._impl.composites.contextmenu import ContextMenu as _InternalContextMenu
from bootstack.widgets._impl.composites.contextmenu import ContextMenuItem

_TRIGGER_MAP: dict[str | None, str | None] = {
    "right_click":  "right-click",
    "left_click":   "left-click",
    "double_click": "double-click",
    "manual":       None,
    None:           None,
}
_VALID_TRIGGERS = frozenset(_TRIGGER_MAP)


def _resolve_tk(widget: Any) -> Any:
    """Return the underlying Tk widget from a public wrapper or pass through."""
    return getattr(widget, "_internal", widget)


class ContextMenu:
    """A popup menu that attaches to a target widget and opens on a gesture or manual call.

    The menu renders as a themed floating popup on Windows and Linux, and as a
    native system menu on macOS. The public API is identical across platforms.

    Args:
        target: Widget the menu attaches to for positioning and auto-trigger
            binding. Accepts public bootstack widgets or raw Tk widgets.
            If omitted, call `show(position=(x, y))` manually.
        min_width: Minimum menu width in pixels. Default `150`.
        trigger: Gesture that auto-shows the menu on `target` — `'right_click'`
            (default), `'left_click'`, `'double_click'`, or `None` (manual only,
            call `show()` yourself).
        on_select: Callback fired whenever any item is activated. Receives a dict
            with `'type'` (str), `'text'` (str), and `'value'` (Any) keys.
        items: Initial list of `ContextMenuItem` objects to add at construction.
        density: Item density — `'default'` or `'compact'`.
        parent: Parent widget for the Tk hierarchy. Defaults to `target`.
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

        if trigger not in _VALID_TRIGGERS:
            valid = ", ".join(repr(k) for k in _VALID_TRIGGERS if k is not None)
            raise ValueError(f"Invalid trigger {trigger!r}. Valid values: {valid}")

        internal_kwargs: dict[str, Any] = {
            "minwidth": min_width,
            "trigger": _TRIGGER_MAP[trigger],
            "density": density,
        }
        if on_select is not None:
            internal_kwargs["command"] = on_select
        if items is not None:
            internal_kwargs["items"] = items
        if tk_target is not None:
            internal_kwargs["target"] = tk_target

        self._internal = _InternalContextMenu(tk_master, **internal_kwargs)
        self._radio_var: Any = None  # shared StringVar for all radio items

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
            shortcut: Keyboard shortcut hint displayed on the right. Accepts a
                modifier pattern (`'Mod+S'` → `'Ctrl+S'` / `'⌘S'`), a key
                registered with the Shortcuts service, or a literal string.
            disabled: If `True`, item is visible but non-interactive.
            key: Unique string identifier. Auto-generated if omitted.

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
        self._internal.add_command(**kw)
        return self._internal.keys()[-1]

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
            value: Initial checked state. Default `False`.
            on_click: Callback fired when the item is toggled.
            key: Unique string identifier. Auto-generated if omitted.

        Returns:
            The key assigned to this item.
        """
        kw: dict[str, Any] = {"text": label, "value": value}
        if on_click is not None:
            kw["command"] = on_click
        if key is not None:
            kw["key"] = key
        self._internal.add_checkbutton(**kw)
        return self._internal.keys()[-1]

    def add_radio_item(
        self,
        label: str,
        *,
        value: Any = None,
        on_click: Callable[[], Any] | None = None,
        key: str | None = None,
    ) -> str:
        """Add a radiobutton item.

        All radio items in a menu share one group — selecting one deselects
        the others. Use check items if you need independent toggles.

        Args:
            label: Item label text.
            value: Value passed to `on_select` when this item is selected.
            on_click: Callback fired when the item is selected.
            key: Unique string identifier. Auto-generated if omitted.

        Returns:
            The key assigned to this item.
        """
        import tkinter
        if self._radio_var is None:
            self._radio_var = tkinter.StringVar()
        kw: dict[str, Any] = {"text": label, "variable": self._radio_var}
        if value is not None:
            kw["value"] = value
        if on_click is not None:
            kw["command"] = on_click
        if key is not None:
            kw["key"] = key
        self._internal.add_radiobutton(**kw)
        return self._internal.keys()[-1]

    def add_separator(self, *, key: str | None = None) -> str:
        """Add a horizontal separator.

        Args:
            key: Unique string identifier. Auto-generated if omitted.

        Returns:
            The key assigned to this separator.
        """
        kw: dict[str, Any] = {}
        if key is not None:
            kw["key"] = key
        self._internal.add_separator(**kw)
        return self._internal.keys()[-1]

    def add_items(self, items: list[ContextMenuItem | dict[str, Any]]) -> None:
        """Add multiple items at once.

        Args:
            items: List of `ContextMenuItem` objects or dicts with a `type` key
                and item kwargs. Valid types: `'command'`, `'checkbutton'`,
                `'radiobutton'`, `'separator'`.
        """
        self._internal.add_items(items)

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

    # ----- Display / lifecycle -----

    def show(self, position: tuple[int, int] | None = None) -> "ContextMenu":
        """Show the menu, optionally at an explicit screen position.

        Args:
            position: Screen `(x, y)` coordinates. If omitted, the menu is
                positioned relative to its `target` widget.

        Returns:
            `self` — allows chaining: `menu.add_item("Edit").show()`.
        """
        self._internal.show(position)
        return self

    def hide(self) -> None:
        """Hide the menu without destroying it."""
        self._internal.hide()

    def destroy(self) -> None:
        """Destroy the menu and release all resources."""
        self._internal.destroy()