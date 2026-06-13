from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Literal, overload, TYPE_CHECKING

from bootstack.events import Event, Subscription
from bootstack.streams import Stream
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._impl.composites.avatar import Avatar as _InternalAvatar
from bootstack.widgets.types import AccentToken

if TYPE_CHECKING:
    from bootstack.images import Image

AvatarShape = Literal["circle", "rounded", "square"]


class Avatar(PublicWidgetBase):
    """A small identity badge — a picture or initials on a filled tile.

    Shows `image` cover-fit and clipped to the avatar shape; when no image is
    given (or one fails to load), it falls back to initials on a `background`
    tile. Initials come from `initials` if given, otherwise from `name` (the
    first letters of the first and last words).

    Args:
        image: The picture to show — an `Image` handle, a file path, or a PIL
            image. Omit to show initials instead.
        name: A name to derive initials from, e.g. `'Ada Lovelace'` → `'AL'`.
            Used when `image` is absent and `initials` is not given.
        initials: Explicit initials (1–2 characters), overriding `name`.
        size: The avatar's edge length in pixels (it is square). Default `40`.
        shape: `'circle'` (default), `'rounded'`, or `'square'`.
        background: Tile color behind initials (and the fallback when an image
            can't load) — a theme color token or a hex string. Default
            `'primary'`.
        foreground: Initials text color — a theme color token or hex string.
            Default `'white'`.
        parent: Override the context-stack parent.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        image: "Image | str | Path | None" = None,
        *,
        name: str | None = None,
        initials: str | None = None,
        size: int = 40,
        shape: AvatarShape = "circle",
        background: AccentToken | str = "primary",
        foreground: str = "white",
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        self._source = self._coerce_image(image)
        self._internal = _InternalAvatar(
            tk_master, source=self._source, name=name, initials=initials,
            size=size, shape=shape, background=background, foreground=foreground,
        )
        self._attach_to_parent(layout_kw)

    @staticmethod
    def _coerce_image(image: "Image | str | Path | None") -> Any:
        if image is None:
            return None
        from bootstack.images import Image as _ImageHandle

        if isinstance(image, _ImageHandle):
            return image
        if isinstance(image, (str, Path)):
            return _ImageHandle.open(image)
        try:
            from PIL.Image import Image as _PILImage

            if isinstance(image, _PILImage):
                return _ImageHandle.from_pil(image)
        except Exception:
            pass
        raise TypeError(
            "Avatar image must be an Image handle, a file path, or a PIL image; "
            f"got {type(image).__name__}"
        )

    # ----- Properties -----

    @property
    def image(self) -> "Image | None":
        """The displayed image handle, or `None` when showing initials.

        Assign an `Image`, a file path, or `None` to change what is shown.
        """
        return self._source

    @image.setter
    def image(self, value: "Image | str | Path | None") -> None:
        self._source = self._coerce_image(value)
        self._internal.set_source(self._source)

    def set_initials(self, *, name: str | None = None, initials: str | None = None) -> None:
        """Update the initials shown (when no image is set).

        Args:
            name: A name to derive initials from.
            initials: Explicit initials, overriding `name`.
        """
        self._internal.set_text(name=name, initials=initials)

    # ----- Events -----

    @overload
    def on_click(self) -> Stream: ...
    @overload
    def on_click(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_click(
        self, handler: Callable[[Event], Any] | None = None
    ) -> Stream | Subscription:
        """Register a callback for clicks on the avatar.

        The handler receives a curated :class:`~bootstack.events.Event`.

        Args:
            handler: Called with the click `Event`. Omit to get a composable
                :class:`~bootstack.streams.Stream`.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("click", handler)


register_widget_events(Avatar, {"click": "<<AvatarClick>>"})
