from __future__ import annotations

from typing import Any, Callable, Literal, overload

from bootstack.widgets._impl.composites.buttongroup import ButtonGroup as _InternalButtonGroup
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.events import ButtonGroupClickEvent, Subscription
from bootstack.streams import Stream
from bootstack.widgets.types import AccentToken, Event, WidgetDensity, Orient, IconPosition, ButtonVariant

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
        orient: Layout orientation. Default `'horizontal'`.
        accent: Accent token applied to all buttons.
        variant: Style variant. Default `'solid'`.
        density: Widget density. Default `'default'`.
        disabled: If `True`, all buttons are non-interactive.
        localize: Whether button labels are translated through the catalog —
            `True`, `False`, or `'auto'` (translate when a translation is
            registered, otherwise show the literal). Defaults to the app's
            `localize_mode`. Set `False` to keep proper nouns untranslated;
            override a single button with `add(..., localize=...)`.
        parent: Override the context-stack parent.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        orient: Orient = "horizontal",
        *,
        accent: AccentToken | str | None = None,
        variant: ButtonVariant = "default",
        density: WidgetDensity = "default",
        disabled: bool = False,
        localize: bool | Literal['auto'] | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._localize = localize
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
        icon_position: IconPosition = "left",
        disabled: bool = False,
        localize: bool | Literal['auto'] | None = None,
        **kwargs: Any,
    ) -> str:
        """Add a button to the group.

        Args:
            label: Button label text.
            key: Unique string key. Auto-generated if omitted.
            icon: Bootstrap Icons name (e.g. `'save'`, `'trash'`).
            icon_position: Position of the icon relative to the label. Ignored
                when `icon_only` is inferred or explicitly set. Default `'left'`.
            disabled: If `True`, this button starts disabled.
            localize: Translation mode for this button's label, overriding the
                group's `localize=`. Defaults to the group setting.

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
        item_localize = localize if localize is not None else self._localize
        if item_localize is not None:
            btn_kwargs["localize"] = item_localize
        btn_kwargs.update(kwargs)

        _key = key
        _group = self

        def _command() -> None:
            btn = _group._internal.item(_key)
            _group.emit("click", data=ButtonGroupClickEvent(
                key=_key,
                text=str(btn.cget("text") or ""),
                icon=btn.configure_style_options("icon"),
            ))

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
            option: Option name to query (e.g. `'text'`, `'state'`).
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
    def on_click(self, handler: Callable[[ButtonGroupClickEvent], Any]) -> Subscription: ...
    def on_click(self, handler: Callable[[ButtonGroupClickEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when any button in the group is clicked.

        Args:
            handler: Called with a :class:`~bootstack.events.ButtonGroupClickEvent`
                (`key`, `text`, `icon` of the clicked button). Omit to get a
                composable :class:`~bootstack.streams.Stream`.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        if handler is None:
            return self.on("click")

        return self.on("click", handler)


register_widget_events(ButtonGroup, _BUTTONGROUP_EVENTS)