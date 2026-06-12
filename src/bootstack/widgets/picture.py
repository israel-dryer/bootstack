from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Literal, overload, TYPE_CHECKING

from bootstack.events import ImageErrorEvent, ImageLoadEvent, Event, Subscription
from bootstack.streams import Stream
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._impl.composites.picture import Picture as _InternalPicture
from bootstack.widgets.types import Anchor, Padding, SurfaceToken

if TYPE_CHECKING:
    from bootstack.images import Image

ImageFit = Literal["contain", "cover", "fill", "none", "scale-down"]


class Picture(PublicWidgetBase):
    """Displays an image, scaled to fit, with optional animation.

    `Picture` is the display widget for pictures and media — the counterpart to
    an `Image`, which is only a source handle. Hand it an `Image` (or a file
    path) and it renders the picture into a resizable area, scaling it to fit
    with a chosen policy. Animated GIF and WebP sources play automatically.

    Unlike showing an image on a `Label`, a `Picture` is sizing-aware: it fills
    the space it is given and re-fits the picture as that space changes, so it
    works in responsive layouts.

    Args:
        image: The picture to show — an `Image` handle (from `bootstack.images`),
            a file path (`str` or `Path`, opened for you), or `None` for an empty
            frame. Assign the `image` property later to change it.
        fit: How the picture is scaled into the display area. Default
            `'contain'`.

            - `'contain'` — scale to fit inside, preserving aspect ratio
              (letterboxing any remainder).
            - `'cover'` — scale to fill, preserving aspect ratio (cropping the
              overflow).
            - `'fill'` — stretch to fill, ignoring aspect ratio.
            - `'none'` — show at natural size, no scaling.
            - `'scale-down'` — like `'contain'`, but never enlarge past natural
              size.
        width: Fixed display width in pixels. Omit to size from the container.
        height: Fixed display height in pixels. Omit to size from the container.
        anchor: Where the picture sits within the area when it does not fill it
            (with `'contain'`, `'scale-down'`, or `'none'`). Default `'center'`.
        corner_radius: Rounded-corner radius in pixels. `0` (default) is square.
        autoplay: Start playing an animated source as soon as it is shown.
            Default `True`.
        loop: Loop an animated source. Default `True`.
        surface: Background surface token used to letterbox behind the picture.
        parent: Explicit parent widget. If omitted, the current context-stack
            container is used.
        **kwargs: Layout placement options applied by the parent container
            (e.g. `fill`, `expand`, `row`, `column`). See :doc:`/tasks/layout`.
    """

    _internal_class = _InternalPicture

    def __init__(
        self,
        image: "Image | str | Path | None" = None,
        *,
        fit: ImageFit = "contain",
        width: int | None = None,
        height: int | None = None,
        anchor: Anchor = "center",
        corner_radius: int = 0,
        autoplay: bool = True,
        loop: bool = True,
        surface: SurfaceToken | str | None = None,
        padding: Padding | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "fit": fit,
            "anchor": anchor,
            "corner_radius": corner_radius,
            "autoplay": autoplay,
            "loop": loop,
            "img_width": width,
            "img_height": height,
        }
        if surface is not None:
            internal_kwargs["surface"] = surface
        if padding is not None:
            internal_kwargs["padding"] = padding
        internal_kwargs.update(kwargs)

        self._source = self._coerce_image(image)
        self._internal = self._internal_class(
            tk_master, source=self._source, **internal_kwargs
        )
        self._attach_to_parent(layout_kw)

    @staticmethod
    def _coerce_image(image: "Image | str | Path | None") -> Any:
        """Normalize an `image=` argument to an `Image` handle (or None)."""
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
            "Picture image must be an Image handle, a file path, or a PIL image; "
            f"got {type(image).__name__}"
        )

    # ----- Properties -----

    @property
    def image(self) -> "Image | None":
        """The displayed image handle, or `None` when empty.

        Assign an `Image`, a file path, or `None` to change what is shown.
        """
        return self._source

    @image.setter
    def image(self, value: "Image | str | Path | None") -> None:
        self._source = self._coerce_image(value)
        self._internal.set_source(self._source)

    @property
    def fit(self) -> ImageFit:
        """The fit policy controlling how the picture is scaled into its area."""
        return self._internal._fit

    @fit.setter
    def fit(self, value: ImageFit) -> None:
        self._internal.set_fit(value)

    @property
    def is_playing(self) -> bool:
        """Whether an animated source is currently playing."""
        return self._internal.is_playing

    # ----- Playback -----

    def play(self) -> None:
        """Start or resume playback of an animated source.

        Has no effect on a still image or when already playing.
        """
        self._internal.play()

    def pause(self) -> None:
        """Pause playback on the current frame.

        Resume with `play`; the frame stays on screen meanwhile.
        """
        self._internal.pause()

    def stop(self) -> None:
        """Stop playback and reset to the first frame."""
        self._internal.stop()

    # ----- Events -----

    @overload
    def on_load(self) -> Stream: ...
    @overload
    def on_load(self, handler: Callable[[ImageLoadEvent], Any]) -> Subscription: ...
    def on_load(
        self, handler: Callable[[ImageLoadEvent], Any] | None = None
    ) -> Stream | Subscription:
        """Register a callback fired when an image is decoded and displayed.

        The handler receives an :class:`~bootstack.events.ImageLoadEvent` with
        the picture's natural `width`, `height`, and frame count.

        Args:
            handler: Called with the load event. Omit to get a composable
                :class:`~bootstack.streams.Stream`.

        Returns:
            A :class:`~bootstack.events.Subscription` when a handler is given,
            otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("load", handler)

    @overload
    def on_error(self) -> Stream: ...
    @overload
    def on_error(self, handler: Callable[[ImageErrorEvent], Any]) -> Subscription: ...
    def on_error(
        self, handler: Callable[[ImageErrorEvent], Any] | None = None
    ) -> Stream | Subscription:
        """Register a callback fired when an image fails to load or decode.

        The handler receives an :class:`~bootstack.events.ImageErrorEvent`
        carrying a human-readable `message`.

        Args:
            handler: Called with the error event. Omit to get a composable
                :class:`~bootstack.streams.Stream`.

        Returns:
            A :class:`~bootstack.events.Subscription` when a handler is given,
            otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("error", handler)

    @overload
    def on_click(self) -> Stream: ...
    @overload
    def on_click(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_click(
        self, handler: Callable[[Event], Any] | None = None
    ) -> Stream | Subscription:
        """Register a callback for clicks on the picture.

        The handler receives a curated :class:`~bootstack.events.Event`.

        Args:
            handler: Called with the click `Event`. Omit to get a composable
                :class:`~bootstack.streams.Stream`.

        Returns:
            A :class:`~bootstack.events.Subscription` when a handler is given,
            otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("click", handler)


register_widget_events(
    Picture,
    {
        "load": "<<PictureLoad>>",
        "error": "<<PictureError>>",
        "click": "<<PictureClick>>",
    },
)
