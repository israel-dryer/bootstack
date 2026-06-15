from __future__ import annotations

from typing import overload, Any, Callable, Literal, TYPE_CHECKING

from bootstack.widgets._impl.primitives.label import Label as _InternalLabel
from bootstack.widgets._impl.primitives.badge import Badge as _InternalBadge
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._core.icon_image_props import IconProperty, ImageProperty
from bootstack.events import Event, Subscription
from bootstack.streams import Stream
from bootstack.widgets.types import (
    AccentToken, VariantToken, SurfaceToken,
    Anchor, Justify, Relief, CompoundMode, Padding, IconPosition, IconSpec,
)

if TYPE_CHECKING:
    from bootstack.signals import Signal


class Label(IconProperty, ImageProperty, PublicWidgetBase):
    """Static text display with optional icon, semantic styling, and font tokens.

    The display text is the first positional argument. All options are
    keyword-only.

    Args:
        text: Text to display.
        textsignal: Reactive `Signal` bound to the display text. Updates
            automatically when the signal changes. Combine with
            `value_format=` to format numeric or date values.
        value_format: Format applied to the `textsignal` value before display —
            a named preset (e.g. `'decimal'`, `'currency'`, `'shortDate'`) or a
            custom pattern (e.g. `'#,##0'`). Requires `textsignal=` and
            localization enabled. See :ref:`format specs <value-formats>`.
        image: An `Image` handle (from `bootstack.images`) to display, for custom
            artwork rather than a Bootstrap Icon name. Also accepts a `get_icon`
            result. Use `icon_position=` to control placement relative to text.
        icon: Bootstrap Icons name (e.g. `'house'`, `'gear'`) — see the full
            catalog at https://icons.getbootstrap.com — or an `IconSpec` mapping
            (`{'name', 'size', 'color'}`) for control over size and color.
        icon_only: If `True`, show only the icon. Auto-detected when
            `text` is empty and `icon` is provided.
        icon_position: Position of the icon or image relative to the text.
            Only relevant when an icon or image is shown alongside text.
            Default `'left'`.
        anchor: Content alignment within the label area. Default `'center'`.
        justify: Multi-line text alignment.
        padding: Inner spacing around the text content.
        width: Width in character units.
        wrap_width: Maximum pixel width before text wraps. Set to enable
            multi-line wrapping.
        font: Semantic font token. Examples: `'body'`, `'heading-lg'`,
            `'heading-md[bold]'`, `'caption'`, `'code'`, `'body+2[italic]'`.
        accent: Semantic color applied to the text.
        variant: Style variant token.
        surface: Background surface context.
        localize: Whether the text is translated through the catalog — `True`,
            `False`, or `'auto'` (translate when a translation is registered,
            otherwise show the literal). Defaults to the app's `localize_mode`.
            Set `False` to keep a proper noun or identifier untranslated.
        parent: Explicit parent widget. If omitted, the current context-stack
            container is used.
    """

    _internal_class = _InternalLabel

    def __init__(
        self,
        text: str = "",
        *,
        textsignal: "Signal | None" = None,
        value_format: str | None = None,
        image: Any = None,
        icon: str | IconSpec | None = None,
        icon_only: bool = False,
        icon_position: IconPosition = "left",
        anchor: Anchor | None = None,
        justify: Justify | None = None,
        padding: Padding | None = None,
        width: int | None = None,
        wrap_width: int | None = None,
        font: str | None = None,
        accent: AccentToken | Literal['muted'] | str | None = None,
        variant: VariantToken | str | None = None,
        surface: SurfaceToken | str | None = None,
        localize: bool | Literal['auto'] | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {}
        if text:
            internal_kwargs["text"] = text
        if textsignal is not None:
            internal_kwargs["textsignal"] = textsignal
        if value_format is not None:
            internal_kwargs["value_format"] = value_format
        deferred_image = None
        if image is not None:
            from bootstack.images import Image as _ImageHandle

            if isinstance(image, _ImageHandle):
                deferred_image = image
                has_text = bool(text) or textsignal is not None
                if not has_text or icon_only:
                    internal_kwargs["icon_only"] = True
                    internal_kwargs["compound"] = "image"
                else:
                    internal_kwargs["compound"] = icon_position
            else:
                internal_kwargs["image"] = image
        if icon is not None:
            internal_kwargs["icon"] = icon
            has_text = bool(text) or textsignal is not None
            if not has_text or icon_only:
                internal_kwargs["icon_only"] = True
                internal_kwargs["compound"] = "image"
            else:
                internal_kwargs["compound"] = icon_position
        elif icon_only:
            internal_kwargs["icon_only"] = True
        if anchor is not None:
            internal_kwargs["anchor"] = anchor
        if justify is not None:
            internal_kwargs["justify"] = justify
        if padding is not None:
            internal_kwargs["padding"] = padding
        if width is not None:
            internal_kwargs["width"] = width
        if wrap_width is not None:
            internal_kwargs["wraplength"] = wrap_width
        if font is not None:
            internal_kwargs["font"] = font
        if accent is not None:
            internal_kwargs["accent"] = accent
        if variant is not None:
            internal_kwargs["variant"] = variant
        if surface is not None:
            internal_kwargs["surface"] = surface
        if localize is not None:
            internal_kwargs["localize"] = localize

        self._internal = self._internal_class(tk_master, **internal_kwargs)
        if deferred_image is not None:
            from bootstack.widgets._core.image_binding import bind_image

            bind_image(self, self._internal, deferred_image)
        self._attach_to_parent(layout_kw)

    # ----- Properties -----

    @property
    def text(self) -> str:
        """The displayed text."""
        return str(self._internal.cget("text"))

    @text.setter
    def text(self, value: str) -> None:
        self._internal.configure(text=value)

    # ----- Events -----

    @overload
    def on_click(self) -> Stream: ...
    @overload
    def on_click(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_click(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback for click events on this label.

        Called with no handler, returns a composable `Stream`. Called with
        a handler, binds it immediately and returns a `Subscription`. The
        handler receives the curated `Event` (pointer position, modifier keys).

        Args:
            handler: Called with the click `Event` when the label is clicked.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("click", handler)


register_widget_events(Label, {})


class Badge(Label):
    """Compact styled chip for status indicators, counts, and tags.

    A `Badge` is a styled `Label` with a fixed visual shape. It accepts the
    same kwargs as `Label`, but the icon and image elements are not rendered.

    Args:
        text: Text to display inside the badge.
        accent: Color intent token for the badge. Defaults to `'primary'`.
        variant: Shape variant — `'square'` is a rounded rectangle, `'pill'` is
            fully rounded. Default `'square'`.
        **kwargs: Other `Label` options (e.g. `font`, `padding`, `width`) plus
            layout placement options applied by the parent container. See
            :doc:`/tasks/layout`.
    """

    _internal_class = _InternalBadge

    def __init__(
        self,
        text: str = "",
        *,
        accent: AccentToken | str = "primary",
        variant: Literal["square", "pill"] = "square",
        **kwargs: Any,
    ) -> None:
        super().__init__(text, accent=accent, variant=variant, **kwargs)


register_widget_events(Badge, {})
