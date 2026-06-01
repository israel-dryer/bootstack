from __future__ import annotations

import tkinter
from typing import Any, Callable, Literal, overload

from bootstack.widgets._impl.composites.list.listview import ListView as _InternalListView
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._core.subscription import Subscription
from bootstack.widgets._core.stream import Stream
from bootstack.widgets.types import AccentToken, WidgetDensity


class ListView(PublicWidgetBase):
    """A virtual-scrolling list for efficiently displaying large datasets.

    Renders only visible rows, making it suitable for thousands of records.
    Populate via ``items=`` (a plain list of dicts) or ``data_source=`` (a
    ``DataSourceProtocol`` for database-backed or API-backed data).

    Each record dict should have an ``'id'`` key; one is auto-generated if absent.
    Displayed fields are ``'title'``, ``'text'``, ``'icon'``, and ``'badge'``.
    Other keys are stored and returned by ``get_selected()`` and events but
    are not rendered.

    Args:
        items: Initial list of record dicts.
        data_source: ``DataSourceProtocol`` implementation for database-backed
            or API-backed data.
        selection_mode: ``'none'`` (default) — no selection; ``'single'`` —
            one item at a time; ``'multi'`` — multiple items.
        show_selection_controls: If ``True``, show checkboxes (multi) or radio
            buttons (single) alongside each item.
        show_chevron: If ``True``, show a right-pointing chevron on each item.
        allow_remove: If ``True``, show a remove button on each item.
        allow_reorder: If ``True``, show a drag handle and allow reordering
            by dragging.
        striped: If ``True``, alternate the row background color.
        show_separators: If ``True`` (default), draw a separator line between
            items.
        show_scrollbar: If ``True`` (default), show the vertical scrollbar.
            Mousewheel scrolling works regardless.
        height: Fixed height in pixels. When set, the list maintains this
            height regardless of its children, making it self-contained for
            scrolling without requiring the parent layout to provide a
            vertical constraint. The widget can still grow beyond this height
            if placed with ``expand=True`` in a constrained parent.
        density: Row height. ``'default'`` (default) or ``'compact'``.
        accent: Color intent token for the selection highlight and drag
            indicator. One of ``'primary'``, ``'secondary'``, ``'info'``,
            ``'success'``, ``'warning'``, ``'danger'``.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        *,
        items: list | None = None,
        data_source: Any = None,
        selection_mode: Literal["none", "single", "multi"] = "none",
        show_selection_controls: bool = False,
        show_chevron: bool = False,
        allow_remove: bool = False,
        allow_reorder: bool = False,
        striped: bool = False,
        show_separators: bool = True,
        show_scrollbar: bool = True,
        height: int | None = None,
        density: WidgetDensity = "default",
        accent: AccentToken | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
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
            "density": density,
        }
        if items is not None:
            internal_kwargs["items"] = items
        if data_source is not None:
            internal_kwargs["datasource"] = data_source
        if accent is not None:
            internal_kwargs["accent"] = accent
        internal_kwargs.update(kwargs)

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

    def get_selected(self) -> list[dict]:
        """Return currently selected records as a list of dicts."""
        return self._internal.get_selected()

    def select_all(self) -> None:
        """Select all items. Only effective when `selection_mode='multi'`."""
        self._internal.select_all()

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
    def on_item_click(self, handler: Callable[[tkinter.Event], Any]) -> Subscription: ...
    def on_item_click(self, handler=None):
        """Fired when an item is clicked. ``event.data`` is the record dict.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("item_click", handler)

    @overload
    def on_selection_changed(self) -> Stream: ...
    @overload
    def on_selection_changed(self, handler: Callable[[tkinter.Event], Any]) -> Subscription: ...
    def on_selection_changed(self, handler=None):
        """Fired when the selection changes. Call ``get_selected()`` to read it.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("selection_changed", handler)

    @overload
    def on_item_delete(self) -> Stream: ...
    @overload
    def on_item_delete(self, handler: Callable[[tkinter.Event], Any]) -> Subscription: ...
    def on_item_delete(self, handler=None):
        """Fired after an item is removed. ``event.data`` is the deleted record.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("item_delete", handler)

    @overload
    def on_item_insert(self) -> Stream: ...
    @overload
    def on_item_insert(self, handler: Callable[[tkinter.Event], Any]) -> Subscription: ...
    def on_item_insert(self, handler=None):
        """Fired after an item is inserted. ``event.data`` is the new record.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("item_insert", handler)

    @overload
    def on_item_update(self) -> Stream: ...
    @overload
    def on_item_update(self, handler: Callable[[tkinter.Event], Any]) -> Subscription: ...
    def on_item_update(self, handler=None):
        """Fired after an item is updated. ``event.data`` is the updated record.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("item_update", handler)

    @overload
    def on_item_drag_start(self) -> Stream: ...
    @overload
    def on_item_drag_start(self, handler: Callable[[tkinter.Event], Any]) -> Subscription: ...
    def on_item_drag_start(self, handler=None):
        """Fired when a drag begins. ``event.data`` includes ``source_index``.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("item_drag_start", handler)

    @overload
    def on_item_drag_end(self) -> Stream: ...
    @overload
    def on_item_drag_end(self, handler: Callable[[tkinter.Event], Any]) -> Subscription: ...
    def on_item_drag_end(self, handler=None):
        """Fired when a drag ends. ``event.data`` includes ``source_index`` and
        ``target_index``.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("item_drag_end", handler)

    # ----- Properties -----

    @property
    def data_source(self) -> Any:
        """The underlying `DataSourceProtocol` instance."""
        return self._internal.get_datasource()


_LISTVIEW_EVENTS: dict[str, str] = {
    "item_click":        "<<ItemClick>>",
    "selection_changed": "<<SelectionChange>>",
    "item_delete":       "<<ItemDelete>>",
    "item_insert":       "<<ItemInsert>>",
    "item_update":       "<<ItemUpdate>>",
    "item_drag_start":   "<<ItemDragStart>>",
    "item_drag_end":     "<<ItemDragEnd>>",
}

register_widget_events(ListView, _LISTVIEW_EVENTS)