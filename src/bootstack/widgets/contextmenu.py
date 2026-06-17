from __future__ import annotations

from typing import Any, Callable, Literal

from bootstack.widgets._impl.composites.contextmenu import ContextMenu as _InternalContextMenu
from bootstack.widgets._impl.composites.contextmenu import ContextMenuItem
from bootstack.widgets.types import WidgetDensity, Anchor
from bootstack.events import MenuSelectEvent

_TRIGGER_MAP: dict[str | None, str | None] = {
    "right_click":  "right-click",
    "left_click":   "left-click",
    "double_click": "double-click",
    "manual":       None,
    None:           None,
}
_VALID_TRIGGERS = frozenset(_TRIGGER_MAP)

# Public item type names → internal ContextMenu type strings.
_ITEM_TYPE_MAP: dict[str, str] = {
    "command":     "command",
    "check":       "checkbutton",
    "radio":       "radiobutton",
    "divider":     "separator",
    # accept the internal names too so existing code doesn't break
    "checkbutton": "checkbutton",
    "radiobutton": "radiobutton",
    "separator":   "separator",
}


def _resolve_item_type(type_: str) -> str:
    resolved = _ITEM_TYPE_MAP.get(type_)
    if resolved is None:
        raise ValueError(
            f"Unknown item type {type_!r}. "
            f"Use 'command', 'check', 'radio', or 'divider'."
        )
    return resolved


def _translate_item(item: Any) -> Any:
    """Translate a public item dict to the internal shape.

    Maps the public `type` name and the public `on_click` callback key to the
    internal equivalents. Non-dict items (`ContextMenuItem` objects) pass through
    unchanged.
    """
    if not isinstance(item, dict):
        return item
    item = dict(item)
    if "type" in item:
        item["type"] = _resolve_item_type(item["type"])
    if "on_click" in item:
        item["command"] = item.pop("on_click")
    return item


def _resolve_tk(widget: Any) -> Any:
    """Return the underlying Tk widget from a public wrapper or pass through."""
    return getattr(widget, "_internal", widget)


class ContextMenu:
    """A popup menu that attaches to a target widget and opens on a gesture or manual call.

    The menu renders as a themed floating popup on Windows and Linux, and as a
    native system menu on macOS. The public API is identical across platforms.

    Args:
        target: Widget the menu attaches to for positioning and auto-trigger
            binding. Accepts any bootstack widget. If omitted, call
            `show(position=(x, y))` manually.
        min_width: Minimum menu width in pixels. Default `150`.
        width: Fixed menu width in pixels. Defaults to auto (uses `min_width`).
        min_height: Minimum menu height in pixels. Defaults to auto.
        height: Fixed menu height in pixels. Defaults to auto-size to content.
        anchor: Point on the menu aligned to `attach` on the target. Default
            `'nw'`.
        attach: Point on the target the menu aligns to. Default `'se'`.
        offset: `(dx, dy)` pixel nudge applied after alignment.
        hide_on_outside_click: Hide the menu when the user clicks outside it.
            Default `True`.
        trigger: Gesture that auto-shows the menu on `target`. `None` means
            manual only — call `show()` yourself. Default `'right_click'`.
        on_select: Callback fired whenever any item is activated. Called with a
            :class:`~bootstack.events.MenuSelectEvent` (`type`, `text`, `value`
            of the activated item).
        items: Initial items — `ContextMenuItem` objects or item dicts (each with
            a `type` key plus item kwargs such as `text`, `icon`, `on_click`).
        density: Item density. Default `'default'`.
        parent: Parent widget for the Tk hierarchy. Defaults to `target`.
    """

    def __init__(
        self,
        target: Any = None,
        *,
        min_width: int = 150,
        width: int | None = None,
        min_height: int | None = None,
        height: int | None = None,
        anchor: Anchor = "nw",
        attach: Anchor = "se",
        offset: tuple[int, int] | None = None,
        hide_on_outside_click: bool = True,
        trigger: Literal["right_click", "left_click", "double_click", "manual"] | None = "right_click",
        on_select: Callable[[MenuSelectEvent], Any] | None = None,
        items: list[Any] | None = None,
        density: WidgetDensity = "default",
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
            "anchor": anchor,
            "attach": attach,
            "hide_on_outside_click": hide_on_outside_click,
        }
        if width is not None:
            internal_kwargs["width"] = width
        if min_height is not None:
            internal_kwargs["minheight"] = min_height
        if height is not None:
            internal_kwargs["height"] = height
        if offset is not None:
            internal_kwargs["offset"] = offset
        if on_select is not None:
            _user_on_select = on_select
            def _on_select(data: dict[str, Any]) -> None:
                _user_on_select(MenuSelectEvent(
                    type=data.get("type", ""),
                    text=data.get("text", ""),
                    value=data.get("value"),
                ))
            internal_kwargs["command"] = _on_select
        if items is not None:
            internal_kwargs["items"] = [_translate_item(it) for it in items]
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

    def add_divider(self, *, key: str | None = None) -> str:
        """Add a horizontal divider.

        Args:
            key: Unique string identifier. Auto-generated if omitted.

        Returns:
            The key assigned to this divider.
        """
        kw: dict[str, Any] = {}
        if key is not None:
            kw["key"] = key
        self._internal.add_separator(**kw)
        return self._internal.keys()[-1]

    def add_items(self, items: list[ContextMenuItem | dict[str, Any]]) -> None:
        """Add multiple items at once.

        Args:
            items: List of `ContextMenuItem` objects or item dicts. Each dict has
                a `type` key (`'command'`, `'check'`, `'radio'`, or `'divider'`)
                plus item kwargs such as `text`, `icon`, `value`, and `on_click`.
        """
        self._internal.add_items([_translate_item(it) for it in items])

    def insert_item(
        self,
        index: int,
        type: str,
        *,
        on_click: Callable[[], Any] | None = None,
        **kwargs: Any,
    ) -> str:
        """Insert an item at a specific position.

        Args:
            index: Zero-based position to insert at.
            type: Item type — `'command'`, `'check'`, `'radio'`, or `'divider'`.
            on_click: Callback fired when the item is activated.
            **kwargs: Other item options (`text`, `icon`, `value`, `disabled`,
                `key`, ...).

        Returns:
            The key assigned to the new item.
        """
        if on_click is not None:
            kwargs["command"] = on_click
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
        """Reconfigure an item after creation.

        Args:
            key: Key returned by an `add_*` method.
            **kwargs: Item options to change (`text`, `icon`, `disabled`,
                `on_click`, ...).
        """
        if "on_click" in kwargs:
            kwargs["command"] = kwargs.pop("on_click")
        self._internal.configure_item(key, **kwargs)

    def item(self, key: str) -> dict[str, Any]:
        """Return an item's current configuration as a dict.

        Args:
            key: Key returned by an `add_*` method.
        """
        return self._internal.item(key)

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