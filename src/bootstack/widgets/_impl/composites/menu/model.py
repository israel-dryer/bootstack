"""Platform-neutral menu model.

The menu bar is built up as data — an ordered list of `MenuGroup`s (File,
Edit, …), each holding a flat list of `MenuItem`s. This is the single source of
truth the platform renderers consume. The model is **single layer**: a group
holds items, and items never hold sub-items (no sub-submenus).

The model is pure data plus shortcut wiring:

- **Display** — every item resolves its `shortcut` to a platform-appropriate
  accelerator string (`shortcut_display`) via the `Shortcuts` service.
- **Binding** — `bind_shortcuts()` registers *pattern* shortcuts
  (e.g. `'Mod+S'`) with the `Shortcuts` service and binds them to a window so
  the keypress actually fires. *Registered keys* (e.g. `'save'`) are treated as
  display-only (their keypress is bound wherever they were registered). This is
  renderer-independent: `tk.Menu` accelerators never bind on their own, and the
  themed strip doesn't either.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Any, Callable, Literal

from bootstack._runtime.shortcuts import (
    classify_shortcut,
    format_shortcut,
    get_shortcuts,
)

MenuItemType = Literal["action", "check", "radio", "separator"]
"""Kind of a menu item.

- `'action'` — a command that fires `on_click` when chosen.
- `'check'` — a toggle with an on/off state.
- `'radio'` — one choice within a named group.
- `'separator'` — a horizontal divider (carries no other fields).
"""

# Process-wide counter so auto-registered pattern shortcuts get unique keys.
_shortcut_seq = itertools.count()


@dataclass
class MenuItem:
    """A single entry in a menu group.

    Only the fields relevant to `type` are meaningful; the rest stay at their
    defaults. `icon` is honored by the Windows/Linux renderer and dropped on
    macOS (native menus are text-only by convention).
    """

    type: MenuItemType = "action"
    """The kind of item — see `MenuItemType`."""
    text: str | None = None
    """Display label. `None` only for separators."""
    icon: str | None = None
    """Icon name (Windows/Linux only; ignored on macOS)."""
    on_click: Callable[[], Any] | None = None
    """Called when the item is chosen (or its shortcut fires)."""
    shortcut: str | None = None
    """A registered shortcut key (display-only) or a pattern (`'Mod+S'`)."""
    disabled: bool = False
    """If `True`, the item is shown dimmed and cannot be chosen."""
    checked: bool = False
    """Initial on/off state for a `'check'` item."""
    value: Any = None
    """The value a `'radio'` item selects within its group."""
    group: str | None = None
    """Radio group name — items sharing a name are mutually exclusive."""
    key: str | None = None
    """Stable identifier for lookup; auto-derived from position if omitted."""

    shortcut_display: str | None = field(default=None, init=False)
    """Resolved accelerator text for display (set in `__post_init__`)."""

    def __post_init__(self) -> None:
        self.shortcut_display = format_shortcut(self.shortcut) or None


class MenuGroup:
    """A top-level menu (e.g. File) holding a flat list of items.

    Usable as a context manager so the builder reads naturally::

        with model.add_menu("File") as file:
            file.add_action("Open", shortcut="Mod+O", on_click=open_file)
    """

    def __init__(self, text: str, *, key: str | None = None) -> None:
        self.text = text
        self.key = key or text
        self.items: list[MenuItem] = []
        self.on_change: Callable[[], Any] | None = None
        """Optional callback fired after any item is added (set by the host
        facade to trigger a coalesced re-render)."""

    # ----- builders -----

    def add_action(
        self,
        text: str,
        *,
        icon: str | None = None,
        on_click: Callable[[], Any] | None = None,
        shortcut: str | None = None,
        disabled: bool = False,
        key: str | None = None,
    ) -> MenuItem:
        """Add a command item that fires `on_click` when chosen."""
        return self._append(
            MenuItem(
                type="action",
                text=text,
                icon=icon,
                on_click=on_click,
                shortcut=shortcut,
                disabled=disabled,
                key=key,
            )
        )

    def add_check(
        self,
        text: str,
        *,
        checked: bool = False,
        on_click: Callable[[], Any] | None = None,
        shortcut: str | None = None,
        disabled: bool = False,
        key: str | None = None,
    ) -> MenuItem:
        """Add a toggle item with an on/off state."""
        return self._append(
            MenuItem(
                type="check",
                text=text,
                checked=checked,
                on_click=on_click,
                shortcut=shortcut,
                disabled=disabled,
                key=key,
            )
        )

    def add_radio(
        self,
        text: str,
        *,
        value: Any = None,
        group: str | None = None,
        on_click: Callable[[], Any] | None = None,
        disabled: bool = False,
        key: str | None = None,
    ) -> MenuItem:
        """Add a radio item — one choice within `group`."""
        return self._append(
            MenuItem(
                type="radio",
                text=text,
                value=value if value is not None else text,
                group=group or self.key,
                on_click=on_click,
                disabled=disabled,
                key=key,
            )
        )

    def add_divider(self, *, key: str | None = None) -> MenuItem:
        """Add a horizontal divider."""
        return self._append(MenuItem(type="separator", key=key))

    # ----- internals -----

    def _append(self, item: MenuItem) -> MenuItem:
        if item.key is None:
            item.key = f"{self.key}.{len(self.items)}"
        self.items.append(item)
        if self.on_change is not None:
            self.on_change()
        return item

    def __enter__(self) -> "MenuGroup":
        return self

    def __exit__(self, *exc: Any) -> bool:
        return False

    def __len__(self) -> int:
        return len(self.items)

    def __repr__(self) -> str:
        return f"MenuGroup(text={self.text!r}, items={len(self.items)})"


# Item dict keys recognized by the declarative `load()` form.
_ITEM_KEYS = frozenset(
    {"type", "text", "icon", "on_click", "shortcut", "disabled", "checked",
     "value", "group", "key"}
)


class MenuModel:
    """The whole menu bar — an ordered list of `MenuGroup`s.

    Build imperatively with `add_menu()`, or declaratively with `load()`; both
    produce the same structure.
    """

    def __init__(self) -> None:
        self.groups: list[MenuGroup] = []
        self._bound_window: Any = None
        self._registered_keys: list[str] = []

    # ----- building -----

    def add_menu(self, text: str, *, key: str | None = None) -> MenuGroup:
        """Append a top-level menu and return it (context-manager capable)."""
        group = MenuGroup(text, key=key)
        self.groups.append(group)
        return group

    def load(self, spec: list[dict]) -> None:
        """Build the model from a declarative spec, replacing any contents.

        Each top-level dict is a menu group: `{"text": ..., "items": [...]}`.
        Each item dict carries `type` (default `'action'`) plus the fields for
        that type. Items must NOT contain a nested `items` key — the model is
        single layer.

        Args:
            spec: List of group dicts.

        Raises:
            ValueError: If an item nests its own `items` (no sub-submenus), or
                an unknown item field is supplied.
        """
        self.clear()
        for raw_group in spec:
            group = self.add_menu(raw_group["text"], key=raw_group.get("key"))
            for raw_item in raw_group.get("items", []):
                self._load_item(group, raw_item)

    @staticmethod
    def _load_item(group: MenuGroup, raw: dict) -> None:
        if "items" in raw:
            raise ValueError(
                "Menu items cannot contain nested 'items' — the menu bar is "
                "single layer (no sub-submenus)."
            )
        unknown = set(raw) - _ITEM_KEYS
        if unknown:
            raise ValueError(
                f"Unknown menu item field(s): {', '.join(sorted(unknown))}. "
                f"Allowed: {', '.join(sorted(_ITEM_KEYS))}."
            )
        item_type = raw.get("type", "action")
        if item_type in ("divider", "separator"):
            group.add_divider(key=raw.get("key"))
        elif item_type == "check":
            group.add_check(
                raw.get("text"),
                checked=raw.get("checked", False),
                on_click=raw.get("on_click"),
                shortcut=raw.get("shortcut"),
                disabled=raw.get("disabled", False),
                key=raw.get("key"),
            )
        elif item_type == "radio":
            group.add_radio(
                raw.get("text"),
                value=raw.get("value"),
                group=raw.get("group"),
                on_click=raw.get("on_click"),
                disabled=raw.get("disabled", False),
                key=raw.get("key"),
            )
        elif item_type == "action":
            group.add_action(
                raw.get("text"),
                icon=raw.get("icon"),
                on_click=raw.get("on_click"),
                shortcut=raw.get("shortcut"),
                disabled=raw.get("disabled", False),
                key=raw.get("key"),
            )
        else:
            raise ValueError(
                f"Unknown menu item type {item_type!r}. Use 'action', 'check', "
                f"'radio', or 'divider'."
            )

    def clear(self) -> None:
        """Remove all groups and release any registered shortcuts."""
        self.unbind_shortcuts()
        self.groups = []

    # ----- iteration -----

    def iter_items(self):
        """Yield every `MenuItem` across all groups, in order."""
        for group in self.groups:
            yield from group.items

    def __len__(self) -> int:
        return len(self.groups)

    def __iter__(self):
        return iter(self.groups)

    # ----- shortcuts -----

    def bind_shortcuts(self, window: Any = None) -> None:
        """Register pattern shortcuts and bind them so keypresses fire.

        Idempotent: previously registered pattern shortcuts are released
        first, then re-registered from the current model. Items whose
        `shortcut` is a *registered key* or a *literal* are left alone (their
        keypress is bound elsewhere, or the text is display-only). Items
        without an `on_click` are skipped — there would be nothing to fire.

        Args:
            window: Window (App/Toplevel) to bind the shortcuts to. If omitted,
                the last window passed to `bind_shortcuts` is reused, if any.
                Shortcuts still register without a window; they bind once one
                is known.
        """
        self.unbind_shortcuts()
        if window is not None:
            self._bound_window = window

        shortcuts = get_shortcuts()
        for item in self.iter_items():
            if not item.shortcut or item.on_click is None:
                continue
            if classify_shortcut(item.shortcut) != "pattern":
                continue  # registered key or literal — bind handled elsewhere
            reg_key = f"__menu_{next(_shortcut_seq)}"
            shortcuts.register(reg_key, item.shortcut, item.on_click)
            self._registered_keys.append(reg_key)

        if self._bound_window is not None:
            shortcuts.bind_to(self._bound_window)

    def unbind_shortcuts(self) -> None:
        """Release every pattern shortcut this model registered."""
        if not self._registered_keys:
            return
        shortcuts = get_shortcuts()
        for reg_key in self._registered_keys:
            try:
                shortcuts.unregister(reg_key)
            except KeyError:
                pass
        self._registered_keys = []

    def __repr__(self) -> str:
        return f"MenuModel(groups={[g.text for g in self.groups]})"