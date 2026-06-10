from __future__ import annotations

from typing import Any, Callable, TYPE_CHECKING, overload

from bootstack.widgets._impl.primitives.button import Button as _InternalButton
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.events import Event, Subscription
from bootstack.streams import Stream
from bootstack.widgets.types import AccentToken, WidgetDensity, IconPosition, ButtonVariant

if TYPE_CHECKING:
    from bootstack.signals import Signal


class Button(PublicWidgetBase):
    """A clickable action trigger.

    The button text is the first positional argument. All styling and
    behavior options are keyword-only.

    Args:
        text: Text displayed on the button.
        on_click: Called with no arguments when the button is clicked.
            Equivalent to subscribing to the ``'click'`` event.
        accent: Color intent token. Defaults to the theme's default button color.
        variant: Visual weight token. Default `'solid'`.
        icon: Bootstrap Icons name (e.g. `'save'`, `'trash'`). See the full
            catalog at https://icons.getbootstrap.com.
        icon_only: If `True`, show only the icon with no text. Inferred
            automatically when `icon=` is set and no text is provided. Set
            meaningful `text` anyway for accessibility.
        icon_position: Position of the icon or image relative to the text.
            Default `'left'`.
        image: An image handle to display on the button, for custom artwork
            rather than a Bootstrap Icon name. (The public image-handle API is
            being finalized for an upcoming release.)
        width: Button width in character units. Useful for making a row of
            buttons uniform width (e.g. `width=10`).
        textsignal: Reactive `Signal[str]` bound to the button text. Updates
            automatically when the signal changes.
        density: Padding density.
        disabled: If `True`, the button is non-interactive and visually dimmed.
        parent: Explicit parent widget. If omitted, the current context-stack
            container is used.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        text: str = "",
        *,
        on_click: Callable[[], Any] | None = None,
        accent: AccentToken | str | None = None,
        variant: ButtonVariant = "default",
        icon: str | None = None,
        icon_only: bool = False,
        icon_position: IconPosition = "left",
        image: Any = None,
        width: int | None = None,
        textsignal: "Signal[str] | None" = None,
        density: WidgetDensity | None = None,
        disabled: bool = False,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        if icon is not None and not text:
            icon_only = True

        internal_kwargs: dict[str, Any] = {"text": text}
        if not icon_only:
            internal_kwargs["compound"] = icon_position
        if on_click is not None:
            internal_kwargs["command"] = on_click
        if accent is not None:
            internal_kwargs["accent"] = accent
        if variant is not None:
            internal_kwargs["variant"] = variant
        if icon is not None:
            internal_kwargs["icon"] = icon
        if icon_only:
            internal_kwargs["icon_only"] = True
        if image is not None:
            internal_kwargs["image"] = image
        if width is not None:
            internal_kwargs["width"] = width
        if textsignal is not None:
            internal_kwargs["textsignal"] = textsignal
        if density is not None:
            internal_kwargs["density"] = density
        if disabled:
            internal_kwargs["state"] = "disabled"

        self._internal = _InternalButton(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Properties -----

    @property
    def text(self) -> str:
        """The button's text."""
        return str(self._internal.cget("text"))

    @text.setter
    def text(self, value: str) -> None:
        self._internal.configure(text=value)

    @property
    def icon(self) -> str | None:
        """Bootstrap Icons name shown on the button, or ``None`` if no icon is set."""
        return self._internal.configure_style_options("icon")

    @icon.setter
    def icon(self, value: str | None) -> None:
        self._internal.configure(icon=value)

    @property
    def disabled(self) -> bool:
        """Whether the button is non-interactive."""
        return str(self._internal.cget("state")) == "disabled"

    @disabled.setter
    def disabled(self, value: bool) -> None:
        self._internal.configure(state="disabled" if value else "normal")

    # ----- Methods -----

    def click(self) -> None:
        """Programmatically invoke the button's command."""
        self._internal.invoke()

    # ----- Events -----

    @overload
    def on_click(self) -> Stream: ...
    @overload
    def on_click(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_click(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback for button click events.

        Called with no handler, returns a composable `Stream`. Called with a
        handler, binds it immediately and returns a `Subscription`.

        For a simple click action prefer the `on_click=` constructor argument,
        which takes a no-argument callback. This method's handler receives the
        curated `Event` (pointer position, modifier keys), consistent with every
        other `on_*` shorthand.

        Args:
            handler: Called with the click :class:`~bootstack.events.Event`
                (pointer position, modifier keys). Omit to get a composable
                :class:`~bootstack.streams.Stream`.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("click", handler)


register_widget_events(Button, {})
