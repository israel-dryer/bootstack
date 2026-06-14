from __future__ import annotations

from typing import Any, Callable, TYPE_CHECKING, overload

from bootstack.widgets._impl.composites.list.listview import ListView as _InternalListView
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.events import Subscription
from bootstack.streams import Stream
from bootstack.widgets.types import AccentToken, Event, WidgetDensity, SelectionMode, ScrollbarVariant

if TYPE_CHECKING:
    from bootstack.data.types import DataSourceProtocol


class ListView(PublicWidgetBase):
    """A virtual-scrolling list for efficiently displaying large datasets.

    Renders only visible rows, making it suitable for thousands of records.
    Populate via `items=` (a plain list of dicts) or `data_source=` (a data
    source for database-backed or API-backed data).

    Each record dict should have an `'id'` key; one is auto-generated if absent.
    Displayed fields are `'title'`, `'text'`, `'icon'`, and `'badge'`. Other
    keys are stored and returned by `selection` and events but are not
    rendered.

    Args:
        items: Initial list of record dicts.
        data_source: A data source for database-backed or API-backed data. Any
            object implementing the data-source protocol is accepted.
        selection_mode: Item selection behavior — `'single'` allows one item at
            a time, `'multi'` allows several. Default `'none'` (no selection).
        show_selection_controls: If `True`, show checkboxes (multi) or radio
            buttons (single) alongside each item.
        select_on_click: Whether clicking an item selects it. Defaults to `True`
            when `selection_mode` is not `'none'`. Set `False` to decouple a
            click (e.g. activate or open) from selection.
        show_chevron: If `True`, show a right-pointing chevron on each item.
        allow_remove: If `True`, show a remove button on each item.
        allow_reorder: If `True`, show a drag handle and allow reordering by
            dragging.
        striped: If `True`, alternate the row background color.
        show_separators: If `True` (default), draw a separator line between
            items.
        show_scrollbar: If `True` (default), show the vertical scrollbar.
            Mousewheel scrolling works regardless.
        scrollbar_variant: Scrollbar style — `'thin'` (default) for a slim bar
            suited to lists, or `'default'` for the standard rounded bar.
        height: Fixed height in pixels. When set, the list maintains this
            height regardless of its children, making it self-contained for
            scrolling without requiring the parent layout to provide a
            vertical constraint. The widget can still grow beyond this height
            if placed with `expand=True` in a constrained parent.
        density: Row height. Default `'default'`.
        accent: Color intent token for the selection highlight and drag
            indicator. Defaults to the theme's default color.
        parent: Override the context-stack parent.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        *,
        items: list[dict] | None = None,
        data_source: DataSourceProtocol | None = None,
        selection_mode: SelectionMode = "none",
        show_selection_controls: bool = False,
        select_on_click: bool | None = None,
        show_chevron: bool = False,
        allow_remove: bool = False,
        allow_reorder: bool = False,
        striped: bool = False,
        show_separators: bool = True,
        show_scrollbar: bool = True,
        scrollbar_variant: ScrollbarVariant = "thin",
        height: int | None = None,
        density: WidgetDensity = "default",
        accent: AccentToken | str | None = None,
        accent_selection: bool = False,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        self._selection_mode = selection_mode
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "selection_mode": selection_mode,
            "show_selection_controls": show_selection_controls,
            "show_chevron": show_chevron,
            "enable_removing": allow_remove,
            "enable_dragging": allow_reorder,
            "striped": striped,
            "show_separator": show_separators,
            "scrollbar_visibility": "always" if show_scrollbar else "never",
            "scrollbar_variant": scrollbar_variant,
            "density": density,
            "accent_selection": accent_selection,
        }
        if items is not None:
            internal_kwargs["items"] = items
        if data_source is not None:
            internal_kwargs["datasource"] = data_source
        if select_on_click is not None:
            internal_kwargs["select_on_click"] = select_on_click
        if accent is not None:
            internal_kwargs["accent"] = accent

        if height is not None and "fill" not in layout_kw:
            layout_kw["fill"] = "x"

        self._internal = _InternalListView(tk_master, **internal_kwargs)
        # Prevent the row pool from feeding back into the layout: without this,
        # adding rows causes the ListView to grow, which gives the Grid more
        # space, which causes more rows to be added — an infinite resize loop.
        self._internal.pack_propagate(False)
        self._attach_to_parent(layout_kw)

        if height is not None:
            self._internal.configure(height=height)

    # ----- Data -----

    def insert_item(self, data: dict) -> None:
        """Insert a new record into the list.

        Args:
            data: Record dict. An `'id'` is auto-generated if absent.
        """
        self._internal.insert_item(data)

    def update_item(self, record_id: Any, data: dict) -> None:
        """Update an existing record.

        Args:
            record_id: ID of the record to update.
            data: Fields to merge into the existing record.
        """
        self._internal.update_item(record_id, data)

    def delete_item(self, record_id: Any) -> None:
        """Delete a record by ID.

        Args:
            record_id: ID of the record to delete.
        """
        self._internal.delete_item(record_id)

    def reload(self) -> None:
        """Reload data from the datasource and refresh the display."""
        self._internal.reload()

    # ----- Selection -----

    @property
    def selection(self) -> dict | list[dict] | None:
        """The selected record(s) — the data bag.

        In `'single'` mode, the selected record `dict` (or `None` when nothing
        is selected). In `'multi'` mode, a `list` of record dicts (empty when
        nothing is selected). Each record carries its non-displayed fields too,
        indexed by key like any record. Read-only.
        """
        rows = self._internal.get_selected()
        if self._selection_mode == "multi":
            return rows
        return rows[0] if rows else None

    def select_items(self, record_ids: list) -> None:
        """Select items by record `id`.

        In `'single'` mode this replaces the current selection; in `'multi'`
        mode the items are added to it.

        Args:
            record_ids: Record ids of the items to select.
        """
        self._internal.select_items(record_ids)

    def select_all(self) -> None:
        """Select all items. Only effective when `selection_mode='multi'`."""
        self._internal.select_all()

    def deselect_items(self, record_ids: list) -> None:
        """Remove the given items from the selection by record `id`.

        Args:
            record_ids: Record ids to deselect.
        """
        self._internal.deselect_items(record_ids)

    def clear_selection(self) -> None:
        """Deselect all items."""
        self._internal.clear_selection()

    # ----- Scrolling -----

    def scroll_to_top(self) -> None:
        """Scroll to the first item."""
        self._internal.scroll_to_top()

    def scroll_to_bottom(self) -> None:
        """Scroll to the last item."""
        self._internal.scroll_to_bottom()

    # ----- Events -----

    @overload
    def on_item_click(self) -> Stream: ...
    @overload
    def on_item_click(self, handler: Callable[[dict[str, Any]], Any]) -> Subscription: ...
    def on_item_click(self, handler: Callable[[dict[str, Any]], Any] | None = None) -> Stream | Subscription:
        """Fired when an item is clicked.

        Args:
            handler: Called with the record `dict` — read fields with
                `e["field"]`. Omit to get a composable
                :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("item_click", handler)

    @overload
    def on_select(self) -> Stream: ...
    @overload
    def on_select(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_select(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Fired when the selection changes.

        Args:
            handler: Called with the curated
                :class:`~bootstack.events.Event`; read `selection` to get
                the current selection. Omit to get a composable
                :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("select", handler)

    @overload
    def on_item_delete(self) -> Stream: ...
    @overload
    def on_item_delete(self, handler: Callable[[dict[str, Any]], Any]) -> Subscription: ...
    def on_item_delete(self, handler: Callable[[dict[str, Any]], Any] | None = None) -> Stream | Subscription:
        """Fired after an item is removed.

        Args:
            handler: Called with the deleted record `dict`. Omit to get a
                composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("item_delete", handler)

    @overload
    def on_item_insert(self) -> Stream: ...
    @overload
    def on_item_insert(self, handler: Callable[[dict[str, Any]], Any]) -> Subscription: ...
    def on_item_insert(self, handler: Callable[[dict[str, Any]], Any] | None = None) -> Stream | Subscription:
        """Fired after an item is inserted.

        Args:
            handler: Called with the new record `dict`. Omit to get a
                composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("item_insert", handler)

    @overload
    def on_item_update(self) -> Stream: ...
    @overload
    def on_item_update(self, handler: Callable[[dict[str, Any]], Any]) -> Subscription: ...
    def on_item_update(self, handler: Callable[[dict[str, Any]], Any] | None = None) -> Stream | Subscription:
        """Fired after an item is updated.

        Args:
            handler: Called with the updated record `dict`. Omit to get a
                composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("item_update", handler)

    @overload
    def on_item_drag_start(self) -> Stream: ...
    @overload
    def on_item_drag_start(self, handler: Callable[[dict[str, Any]], Any]) -> Subscription: ...
    def on_item_drag_start(self, handler: Callable[[dict[str, Any]], Any] | None = None) -> Stream | Subscription:
        """Fired when a drag begins.

        Args:
            handler: Called with the record `dict`, including `source_index`.
                Omit to get a composable :class:`~bootstack.streams.Stream`
                instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("item_drag_start", handler)

    @overload
    def on_item_drag_end(self) -> Stream: ...
    @overload
    def on_item_drag_end(self, handler: Callable[[dict[str, Any]], Any]) -> Subscription: ...
    def on_item_drag_end(self, handler: Callable[[dict[str, Any]], Any] | None = None) -> Stream | Subscription:
        """Fired when a drag ends.

        Args:
            handler: Called with the record `dict`, including `source_index`
                and `target_index`. Omit to get a composable
                :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("item_drag_end", handler)

    # ----- Properties -----

    @property
    def data_source(self) -> DataSourceProtocol:
        """The underlying data source instance."""
        return self._internal.get_datasource()


_LISTVIEW_EVENTS: dict[str, str] = {
    "item_click":        "<<ItemClick>>",
    "select":            "<<SelectionChange>>",
    "item_delete":       "<<ItemDelete>>",
    "item_insert":       "<<ItemInsert>>",
    "item_update":       "<<ItemUpdate>>",
    "item_drag_start":   "<<ItemDragStart>>",
    "item_drag_end":     "<<ItemDragEnd>>",
}

register_widget_events(ListView, _LISTVIEW_EVENTS)