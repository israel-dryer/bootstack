from __future__ import annotations

from typing import Any, Callable, Literal, overload

from bootstack.widgets._impl.composites.buttongroup import ButtonGroup as _InternalButtonGroup
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.events import Subscription
from bootstack.streams import Stream
from bootstack.widgets.types import AccentToken, Event, VariantToken, WidgetDensity

_BUTTONGROUP_EVENTS: dict[str, str] = {
    "click": "<<BsButtonGroupClick>>",
}


class ButtonGroup(PublicWidgetBase):
    """A row (or column) of visually-connected buttons sharing accent and variant.

    Buttons are added via `add()` or `add_all()`. The group propagates
    `accent`, `variant`, and `density` to every member automatically.
    Listen for any button press with `on_click()`, which receives the key
    of the clicked button.

    Args:
        orient: `'horizontal'` (default) or `'vertical'`.
        accent: Accent token applied to all buttons. One of `'primary'`,
            `'secondary'`, `'info'`, `'success'`, `'warning'`, `'danger'`,
            `'default'`.
        variant: Style variant — `'solid'` (default), `'outline'`, `'ghost'`.
        density: Widget density — `'default'` or `'compact'`.
        disabled: If True, all buttons are non-interactive.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        orient: Literal["horizontal", "vertical"] = "horizontal",
        *,
        accent: AccentToken | str | None = None,
        variant: VariantToken | str = "solid",
        density: WidgetDensity | str = "default",
        disabled: bool = False,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "orient": orient,
            "variant": variant,
            "density": density,
        }
        if accent is not None:
            internal_kwargs["accent"] = accent
        if disabled:
            internal_kwargs["state"] = "disabled"

        self._internal = _InternalButtonGroup(tk_master, **internal_kwargs)
        self._key_counter = 0
        self._attach_to_parent(layout_kw)

    # ----- Item management -----

    def add(
        self,
        label: str = "",
        *,
        key: str | None = None,
        icon: str | None = None,
        icon_position: Literal["left", "right", "top", "bottom"] = "left",
        disabled: bool = False,
        **kwargs: Any,
    ) -> str:
        """Add a button to the group.

        Args:
            label: Button label text.
            key: Unique string key. Auto-generated if omitted.
            icon: Bootstrap Icons name (e.g. `'save'`, `'trash'`).
            icon_position: Position of the icon relative to the label. One of
                `'left'` (default), `'right'`, `'top'`, `'bottom'`. Ignored
                when `icon_only` is inferred or explicitly set.
            disabled: If True, this button starts disabled.

        Returns:
            The key assigned to this button.
        """
        if key is None:
            key = f"widget_{self._key_counter}"
            self._key_counter += 1

        icon_only = icon is not None and not label

        btn_kwargs: dict[str, Any] = {}
        if icon is not None:
            btn_kwargs["icon"] = icon
        if icon_only:
            btn_kwargs["icon_only"] = True
        elif icon is not None:
            btn_kwargs["compound"] = icon_position
        if disabled:
            btn_kwargs["state"] = "disabled"
        btn_kwargs.update(kwargs)

        _key = key
        _group = self

        def _command() -> None:
            btn = _group._internal.item(_key)
            _group.emit("click", data={
                "key":  _key,
                "text": str(btn.cget("text") or ""),
                "icon": btn.configure_style_options("icon"),
            })

        self._internal.add(label or None, key=key, command=_command, **btn_kwargs)
        return key

    def add_all(self, items: list) -> list[str]:
        """Add multiple buttons at once.

        Each item is either a label string or a dict of keyword arguments
        accepted by `add()`.

        Args:
            items: List of labels or dicts. A plain string is treated as
                the button label with no other options.

        Returns:
            List of keys assigned to each button, in insertion order.
        """
        return [self.add(**item) if isinstance(item, dict) else self.add(item) for item in items]

    def remove(self, key: str) -> None:
        """Remove the button identified by `key`.

        Args:
            key: Key returned by `add()`.
        """
        self._internal.remove(key)

    def update_item(self, key: str, **kwargs: Any) -> None:
        """Reconfigure a button after creation.

        Args:
            key: Key returned by `add()`.
            **kwargs: Options forwarded to the button's `configure()`.
        """
        self._internal.configure_item(key, **kwargs)

    def query_item(self, key: str, option: str) -> Any:
        """Return the current value of a configuration option for a button.

        Args:
            key: Key returned by `add()`.
            option: Option name to query (e.g. ``'text'``, ``'state'``).
        """
        return self._internal.configure_item(key, option)

    # ----- Queries -----

    def item(self, key: str) -> Any:
        """Return the button item object for `key`.

        Args:
            key: Key returned by `add()`.
        """
        return self._internal.item(key)

    @property
    def items(self) -> tuple[Any, ...]:
        """All button items in insertion order."""
        return self._internal.items()

    @property
    def keys(self) -> tuple[str, ...]:
        """Keys of all buttons in insertion order."""
        return self._internal.keys()

    def __len__(self) -> int:
        """Number of buttons in the group."""
        return len(self._internal)

    def __contains__(self, key: object) -> bool:
        """True if a button with the given key exists in the group."""
        return key in self._internal

    # ----- Properties -----

    @property
    def disabled(self) -> bool:
        """Whether all buttons are non-interactive."""
        return str(self._internal.cget("state")) == "disabled"

    @disabled.setter
    def disabled(self, value: bool) -> None:
        self._internal.configure(state="disabled" if value else "normal")

    # ----- Events -----

    @overload
    def on_click(self) -> Stream: ...
    @overload
    def on_click(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_click(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when any button in the group is clicked.

        Called with no handler, returns a composable `Stream`. Called with a
        handler, binds it immediately and returns a `Subscription`.

        The handler receives a standard event object. ``event.data`` is a dict
        with ``'key'``, ``'text'``, and ``'icon'`` for the clicked button.

        Args:
            handler: Called with the click event. Access ``event.data['key']``,
                ``event.data['text']``, and ``event.data['icon']``.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        if handler is None:
            return self.on("click")

        return self.on("click", handler)


register_widget_events(ButtonGroup, _BUTTONGROUP_EVENTS)