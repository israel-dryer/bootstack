from __future__ import annotations

from typing import Any, Callable, Literal, overload, TYPE_CHECKING

from bootstack.events import Event, Subscription
from bootstack.streams import Stream
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._impl.composites.carousel import Carousel as _InternalCarousel
from bootstack.widgets.types import AccentToken, SurfaceToken

if TYPE_CHECKING:
    from bootstack.data.types import DataSourceProtocol

ImageFit = Literal["contain", "cover", "fill", "none", "scale-down"]
Transition = Literal["slide", "fade", "none"]
Indicator = Literal["dots", "count", "none"]


class Carousel(PublicWidgetBase):
    """Shows one image slide at a time, with prev/next navigation.

    `Carousel` steps through a collection of image records one slide at a time —
    the focus-on-one counterpart to :doc:`Gallery </widgets/gallery>`. It pairs
    naturally with `Gallery.on_item_activate` to open a full-size pop-up viewer:
    a `Carousel` over the same `items`, starting at the activated slide.

    Each record names the image through `image_field` (an `Image`, a file path,
    or a PIL image) and, optionally, a caption through `caption_field`. Navigate
    with the on-screen chevrons, the arrow keys, the indicator dots, or the
    `next`/`previous`/`go_to` methods.

    Args:
        items: Initial list of record dicts.
        data_source: A data source for database- or API-backed data.
        image_field: Record key holding each slide's image. Default `'image'`.
        caption_field: Record key for the caption overlaid on each slide.
            Default `None` (no captions).
        index: The slide shown first. Default `0`.
        fit: How each image is scaled into the stage — `'contain'` (default,
            shows the whole image), `'cover'`, `'fill'`, `'none'`, or
            `'scale-down'`. See :doc:`Picture </widgets/picture>`.
        transition: Animation between slides — `'slide'` (default), `'fade'`, or
            `'none'`.
        show_arrows: Show the overlaid prev/next chevrons. Default `True`.
        indicator: The slide indicator — `'dots'` (default; auto-switches to a
            counter when there are many slides), `'count'`, or `'none'`.
        autoplay: Auto-advance through the slides. Default `False`.
        interval: Autoplay dwell time per slide, in milliseconds. Default `4000`.
        loop: Wrap around past the first and last slides. Default `True`.
        corner_radius: Rounded-corner radius for the slide image, in pixels.
            Default `0`.
        aspect_ratio: Width-to-height ratio used to derive the carousel's minimum
            height when it sits in a container that doesn't impose one (a scroll
            view, an auto-fit window) — a larger ratio gives a wider, shorter
            floor. Default `1.5`. Ignored when `height` is set. `fill`/`expand`
            still grow the stage past this floor.
        height: Explicit minimum height for the slide stage, in pixels. Overrides
            `aspect_ratio`. Default `None` (derive from `aspect_ratio`).
        accent: Color intent token to brand the active indicator dot. By default
            the dots are neutral (white), which reads on any image; set this to
            color the active dot.
        surface: Background surface token shown behind a letterboxed slide.
        parent: Override the context-stack parent.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        *,
        items: list[dict] | None = None,
        data_source: "DataSourceProtocol | None" = None,
        image_field: str = "image",
        caption_field: str | None = None,
        index: int = 0,
        fit: ImageFit = "contain",
        transition: Transition = "slide",
        show_arrows: bool = True,
        indicator: Indicator = "dots",
        autoplay: bool = False,
        interval: int = 4000,
        loop: bool = True,
        corner_radius: int = 0,
        aspect_ratio: float = 1.5,
        height: int | None = None,
        accent: AccentToken | str | None = None,
        surface: SurfaceToken | str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "image_field": image_field,
            "caption_field": caption_field,
            "index": index,
            "fit": fit,
            "transition": transition,
            "show_arrows": show_arrows,
            "indicator": indicator,
            "autoplay": autoplay,
            "interval": interval,
            "loop": loop,
            "corner_radius": corner_radius,
            "aspect_ratio": aspect_ratio,
            "height": height,
        }
        if items is not None:
            internal_kwargs["items"] = items
        if data_source is not None:
            internal_kwargs["datasource"] = data_source
        if accent is not None:
            internal_kwargs["accent"] = accent
        if surface is not None:
            internal_kwargs["surface"] = surface

        self._internal = _InternalCarousel(tk_master, **internal_kwargs)
        self._internal.pack_propagate(False)
        self._attach_to_parent(layout_kw)

    # ----- Navigation -----

    @property
    def index(self) -> int:
        """The index of the currently shown slide. Assign to jump to a slide."""
        return self._internal.index

    @index.setter
    def index(self, value: int) -> None:
        self._internal.go_to(int(value))

    @property
    def current(self) -> dict | None:
        """The currently shown record — the data bag — or `None` when empty."""
        return self._internal.current

    @property
    def count(self) -> int:
        """The number of slides."""
        return self._internal.count

    def next(self) -> None:
        """Advance to the next slide."""
        self._internal.next()

    def previous(self) -> None:
        """Go back to the previous slide."""
        self._internal.previous()

    def go_to(self, index: int) -> None:
        """Jump to the slide at `index`, animating in the right direction.

        Args:
            index: The slide index to show.
        """
        self._internal.go_to(int(index))

    # ----- Autoplay -----

    @property
    def is_playing(self) -> bool:
        """Whether autoplay is currently running."""
        return self._internal.is_playing

    def play(self) -> None:
        """Start auto-advancing through the slides."""
        self._internal.play()

    def pause(self) -> None:
        """Stop auto-advancing."""
        self._internal.pause()

    def stop(self) -> None:
        """Stop auto-advancing and return to the first slide."""
        self._internal.stop()

    # ----- Data -----

    @property
    def data_source(self) -> "DataSourceProtocol":
        """The underlying data source instance."""
        return self._internal.get_datasource()

    def reload(self) -> None:
        """Reload from the data source and refresh the current slide."""
        self._internal.reload()

    # ----- Events -----

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[dict[str, Any]], Any]) -> Subscription: ...
    def on_change(
        self, handler: Callable[[dict[str, Any]], Any] | None = None
    ) -> Stream | Subscription:
        """Fired when the active slide changes.

        Args:
            handler: Called with the now-current record `dict` — read fields with
                `e["field"]`. Omit to get a composable
                :class:`~bootstack.streams.Stream`.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("change", handler)

    @overload
    def on_item_click(self) -> Stream: ...
    @overload
    def on_item_click(self, handler: Callable[[dict[str, Any]], Any]) -> Subscription: ...
    def on_item_click(
        self, handler: Callable[[dict[str, Any]], Any] | None = None
    ) -> Stream | Subscription:
        """Fired when the current slide is clicked.

        The natural hook for closing a pop-up viewer or opening a detail view.

        Args:
            handler: Called with the current record `dict`. Omit to get a
                composable :class:`~bootstack.streams.Stream`.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("item_click", handler)


_CAROUSEL_EVENTS: dict[str, str] = {
    "change": "<<Change>>",
    "item_click": "<<ItemClick>>",
}

register_widget_events(Carousel, _CAROUSEL_EVENTS)
