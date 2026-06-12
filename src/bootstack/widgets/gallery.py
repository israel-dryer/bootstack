from __future__ import annotations

from typing import Any, Callable, Literal, overload, TYPE_CHECKING

from bootstack.events import Event, Subscription
from bootstack.streams import Stream
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._impl.composites.gallery import Gallery as _InternalGallery
from bootstack.widgets.types import AccentToken, SelectionMode, SurfaceToken

if TYPE_CHECKING:
    from bootstack.data.types import DataSourceProtocol

ImageFit = Literal["contain", "cover", "fill", "none", "scale-down"]


class Gallery(PublicWidgetBase):
    """A scrollable, selectable grid of image thumbnails.

    `Gallery` displays a collection of image records as a reflowing grid of
    thumbnails, recycling tiles so it stays efficient for large collections. It
    is record-native — populate it with `items=` (a list of dicts) or a
    `data_source=`, and read the chosen tile(s) back through `selection`, the
    same model `ListView`, `DataTable`, and `Tree` share.

    Each record names the image to show through `image_field` (an `Image`, a file
    path, or a PIL image) and, optionally, a caption through `caption_field`.
    Other keys ride along in the record bag and are returned by `selection` and
    events.

    Args:
        items: Initial list of record dicts.
        data_source: A data source for database- or API-backed data. Any object
            implementing the data-source protocol is accepted.
        image_field: Record key holding the image to display in each tile — an
            `Image` handle, a file path, or a PIL image. Default `'image'`.
        caption_field: Record key for the caption shown under each thumbnail.
            Default `None` (no captions).
        columns: Number of columns, or `'auto'` (default) to reflow the grid to
            fit the available width as it resizes.
        tile_size: Thumbnail size as `(width, height)` in pixels. Default
            `(160, 160)`.
        fit: How each image is scaled into its tile — `'contain'`, `'cover'`
            (default), `'fill'`, `'none'`, or `'scale-down'`. See `Picture`.
        corner_radius: Rounded-corner radius for thumbnails, in pixels. Default
            `0`.
        gap: Spacing between tiles in pixels. Default `8`.
        selection_mode: Tile selection behavior — `'single'`, `'multi'`, or
            `'none'` (default). Selected tiles show an accent highlight ring.
        accent: Color intent token for the selection ring. Defaults to the
            theme's primary color.
        surface: Background surface token shown behind the tiles.
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
        columns: "int | Literal['auto']" = "auto",
        tile_size: tuple[int, int] = (160, 160),
        fit: ImageFit = "cover",
        corner_radius: int = 0,
        gap: int = 8,
        selection_mode: SelectionMode = "none",
        accent: AccentToken | str | None = None,
        surface: SurfaceToken | str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        self._selection_mode = selection_mode
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "image_field": image_field,
            "caption_field": caption_field,
            "columns": columns,
            "tile_size": tile_size,
            "fit": fit,
            "corner_radius": corner_radius,
            "gap": gap,
            "selection_mode": selection_mode,
        }
        if items is not None:
            internal_kwargs["items"] = items
        if data_source is not None:
            internal_kwargs["datasource"] = data_source
        if accent is not None:
            internal_kwargs["accent"] = accent
        if surface is not None:
            internal_kwargs["surface"] = surface

        self._internal = _InternalGallery(tk_master, **internal_kwargs)
        self._internal.pack_propagate(False)
        self._attach_to_parent(layout_kw)

    # ----- Selection -----

    @property
    def selection(self) -> dict | list[dict] | None:
        """The selected record(s) — the data bag.

        In `'single'` mode, the selected record `dict` (or `None`). In `'multi'`
        mode, a `list` of record dicts (empty when nothing is selected). Each
        record carries its non-displayed fields too. Read-only.
        """
        rows = self._internal.get_selected()
        if self._selection_mode == "multi":
            return rows
        return rows[0] if rows else None

    def select_items(self, record_ids: list) -> None:
        """Select tiles by record `id`.

        In `'single'` mode this replaces the current selection; in `'multi'`
        mode the items are added to it.

        Args:
            record_ids: Record ids of the tiles to select.
        """
        self._internal.select_items(record_ids)

    def deselect_items(self, record_ids: list) -> None:
        """Remove the given tiles from the selection by record `id`.

        Args:
            record_ids: Record ids to deselect.
        """
        self._internal.deselect_items(record_ids)

    def select_all(self) -> None:
        """Select all tiles. Only effective when `selection_mode='multi'`."""
        self._internal.select_all()

    def clear_selection(self) -> None:
        """Deselect all tiles."""
        self._internal.clear_selection()

    # ----- Scrolling -----

    def scroll_to_top(self) -> None:
        """Scroll to the first tile."""
        self._internal.scroll_to_top()

    def scroll_to_bottom(self) -> None:
        """Scroll to the last tile."""
        self._internal.scroll_to_bottom()

    def reload(self) -> None:
        """Reload from the data source and refresh the grid."""
        self._internal.reload()

    # ----- Properties -----

    @property
    def data_source(self) -> "DataSourceProtocol":
        """The underlying data source instance."""
        return self._internal.get_datasource()

    # ----- Events -----

    @overload
    def on_item_click(self) -> Stream: ...
    @overload
    def on_item_click(self, handler: Callable[[dict[str, Any]], Any]) -> Subscription: ...
    def on_item_click(
        self, handler: Callable[[dict[str, Any]], Any] | None = None
    ) -> Stream | Subscription:
        """Fired when a tile is clicked.

        Args:
            handler: Called with the record `dict` — read fields with
                `e["field"]`. Omit to get a composable
                :class:`~bootstack.streams.Stream`.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("item_click", handler)

    @overload
    def on_item_activate(self) -> Stream: ...
    @overload
    def on_item_activate(self, handler: Callable[[dict[str, Any]], Any]) -> Subscription: ...
    def on_item_activate(
        self, handler: Callable[[dict[str, Any]], Any] | None = None
    ) -> Stream | Subscription:
        """Fired when a tile is activated (double-clicked).

        The natural hook for opening a full-size viewer or detail page for the
        chosen record.

        Args:
            handler: Called with the record `dict`. Omit to get a composable
                :class:`~bootstack.streams.Stream`.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("item_activate", handler)

    @overload
    def on_select(self) -> Stream: ...
    @overload
    def on_select(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_select(
        self, handler: Callable[[Event], Any] | None = None
    ) -> Stream | Subscription:
        """Fired when the selection changes.

        Args:
            handler: Called with the curated :class:`~bootstack.events.Event`;
                read `selection` for the current selection. Omit to get a
                composable :class:`~bootstack.streams.Stream`.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("select", handler)


_GALLERY_EVENTS: dict[str, str] = {
    "item_click": "<<ItemClick>>",
    "item_activate": "<<ItemActivate>>",
    "select": "<<SelectionChange>>",
}

register_widget_events(Gallery, _GALLERY_EVENTS)
