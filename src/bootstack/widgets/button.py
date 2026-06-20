from __future__ import annotations

from typing import Any, Callable, TYPE_CHECKING, overload

from bootstack.widgets._impl.primitives.button import Button as _InternalButton
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._core.icon_image_props import IconProperty, ImageProperty
from bootstack.events import Event, Subscription
from bootstack.streams import Stream
from bootstack.widgets.types import AccentToken, WidgetDensity, IconPosition, ButtonVariant, IconSpec, LocalizeMode

if TYPE_CHECKING:
    from bootstack.signals import Signal


class Button(IconProperty, ImageProperty, PublicWidgetBase):
    """A clickable action trigger.

    The button text is the first positional argument. All styling and
    behavior options are keyword-only.

    Args:
        text: Text displayed on the button.
        on_click: Called with no arguments when the button is clicked.
            Equivalent to subscribing to the `'click'` event.
        accent: Color intent token. Defaults to the theme's default button color.
        variant: Visual weight token. Default `'solid'`.
        icon: Bootstrap Icons name (e.g. `'save'`, `'trash'`) — see the full
            catalog at https://icons.getbootstrap.com — or an `IconSpec` mapping
            (`{'name', 'size', 'color'}`) for control over size and color.
        icon_only: If `True`, show only the icon with no text. Inferred
            automatically when `icon=` is set and no text is provided. Set
            meaningful `text` anyway for accessibility.
        icon_position: Position of the icon or image relative to the text.
            Default `'left'`.
        image: An `Image` handle (from `bootstack.images`) to display on the
            button, for custom artwork rather than a Bootstrap Icon name. Also
            accepts a `get_icon` result.
        width: Button width in character units. Useful for making a row of
            buttons uniform width (e.g. `width=10`).
        textsignal: Reactive `Signal[str]` bound to the button text. Updates
            automatically when the signal changes.
        density: Padding density.
        disabled: If `True`, the button is non-interactive and visually dimmed.
        localize: Whether the text is translated through the catalog — `True`,
            `False`, or `'auto'`. Defaults to the app's `localize_mode`. Set
            `False` to keep a proper noun or identifier untranslated.
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
        icon: str | IconSpec | None = None,
        icon_only: bool = False,
        icon_position: IconPosition = "left",
        image: Any = None,
        width: int | None = None,
        textsignal: "Signal[str] | None" = None,
        density: WidgetDensity | None = None,
        disabled: bool = False,
        localize: LocalizeMode | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        if icon is not None and not text:
            icon_only = True

        # The internal command is always our dispatcher so that a click —
        # whether by mouse, keyboard (Space/Return), or click()/invoke() — runs
        # the on_click= callback AND emits <<Click>> for on_click() subscribers,
        # consistently and only when the button is enabled (ttk gates the
        # command on state, unlike a raw <Button-1> binding).
        self._on_click_cmd = on_click

        internal_kwargs: dict[str, Any] = {"text": text, "command": self._dispatch_click}
        if not icon_only:
            internal_kwargs["compound"] = icon_position
        if accent is not None:
            internal_kwargs["accent"] = accent
        if variant is not None:
            internal_kwargs["variant"] = variant
        if icon is not None:
            internal_kwargs["icon"] = icon
        if icon_only:
            internal_kwargs["icon_only"] = True
        deferred_image = None
        if image is not None:
            from bootstack.images import Image as _ImageHandle

            if isinstance(image, _ImageHandle):
                deferred_image = image
            else:
                internal_kwargs["image"] = image
        if width is not None:
            internal_kwargs["width"] = width
        if textsignal is not None:
            internal_kwargs["textsignal"] = textsignal
        if density is not None:
            internal_kwargs["density"] = density
        if disabled:
            internal_kwargs["state"] = "disabled"
        if localize is not None:
            internal_kwargs["localize"] = localize

        self._internal = _InternalButton(tk_master, **internal_kwargs)
        if deferred_image is not None:
            from bootstack.widgets._core.image_binding import bind_image

            bind_image(self, self._internal, deferred_image)
        self._attach_to_parent(layout_kw)

    # ----- Properties -----

    @property
    def text(self) -> str:
        """The button's text."""
        # Read through the bound variable when present: with a textsignal/
        # textvariable, ttk's `text` option no longer tracks the displayed text.
        textvar = getattr(self._internal, "_textvariable", None)
        if textvar is not None:
            return str(textvar.get())
        return str(self._internal.cget("text"))

    @text.setter
    def text(self, value: str) -> None:
        # When a textsignal/textvariable owns the text, ttk ignores the `text`
        # option — write through the variable instead (which also keeps the
        # bound signal in sync). Falls back to the option when unbound.
        textvar = getattr(self._internal, "_textvariable", None)
        if textvar is not None:
            textvar.set(value)
        else:
            self._internal.configure(text=value)

    @property
    def disabled(self) -> bool:
        """Whether the button is non-interactive."""
        return self._internal.instate(("disabled",))

    @disabled.setter
    def disabled(self, value: bool) -> None:
        self._internal.configure(state="disabled" if value else "normal")

    # ----- Methods -----

    def click(self) -> None:
        """Programmatically activate the button.

        Runs the same path as a real click: the `on_click=` callback and any
        `on_click()` handlers both fire. Does nothing while the button is
        disabled.
        """
        self._internal.invoke()

    def _dispatch_click(self) -> None:
        """ttk command target — runs on every activation, never while disabled.

        Fires on mouse release over the button, keyboard Space/Return, and
        `click()`/`invoke()`. Runs the constructor `on_click=` callback, then
        emits `<<Click>>` so `on_click()` subscribers see the same activation.
        """
        if self._on_click_cmd is not None:
            self._on_click_cmd()
        # `when='now'` delivers to subscribers synchronously, so a click()/invoke()
        # notifies handlers before it returns (matches the on_click= callback).
        self._internal.event_generate("<<Click>>", when="now")

    # ----- Events -----

    @overload
    def on_click(self) -> Stream: ...
    @overload
    def on_click(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_click(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback for button click events.

        Called with no handler, returns a composable `Stream`. Called with a
        handler, binds it immediately and returns a `Subscription`.

        Fires on activation — a mouse release over the button, a keyboard
        Space/Return while focused, or :meth:`click`/`invoke` — and never while
        the button is disabled, matching the `on_click=` constructor argument.
        For a simple no-argument action prefer that constructor argument; use
        this method (or its `Stream`) to compose the click event.

        Args:
            handler: Called with the click :class:`~bootstack.events.Event`.
                The event marks the activation; because keyboard and
                programmatic activations carry no pointer, treat position and
                modifier fields as unset. Omit the handler to get a composable
                :class:`~bootstack.streams.Stream`.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("click", handler)


# "click" resolves to the <<Click>> virtual event emitted by the command
# dispatcher (see _dispatch_click) rather than the global <Button-1> mapping, so
# both the handler and Stream forms fire on activation and honor disabled state.
register_widget_events(Button, {"click": "<<Click>>"})
