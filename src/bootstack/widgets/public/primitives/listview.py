from __future__ import annotations

from typing import Any, Callable, Literal

from bootstack.widgets.composites.list.listview import ListView as _InternalListView
from bootstack.widgets.public.base import PublicWidgetBase


class ListView(PublicWidgetBase):
    """A virtual-scrolling list for efficiently displaying large datasets.

    Renders only visible rows, making it suitable for thousands of records.
    Populate via `items=` (a plain list of dicts) or `datasource=` (a
    `DataSourceProtocol` for database-backed or API-backed data).

    Each record dict should have an `'id'` key; one is auto-generated if absent.

    Args:
        items: Initial list of record dicts.
        datasource: `DataSourceProtocol` implementation for data access.
        selection_mode: `'none'` (default), `'single'`, or `'multi'`.
        show_selection_controls: Show checkboxes/radio buttons alongside items.
        show_chevron: Show a chevron indicator on each item.
        enable_removing: Show a remove button on each item.
        enable_dragging: Show a drag handle and allow row reordering.
        striped: Alternate row background colors.
        show_separator: Show a separator line between items.
        scrollbar_visibility: `'always'` (default) or `'never'`.
        density: Item density — `'default'` or `'compact'`.
        accent: Accent token for selection and drag indicator.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        *,
        items: list | None = None,
        datasource: Any = None,
        selection_mode: Literal["none", "single", "multi"] = "none",
        show_selection_controls: bool = False,
        show_chevron: bool = False,
        enable_removing: bool = False,
        enable_dragging: bool = False,
        striped: bool = False,
        show_separator: bool = True,
        scrollbar_visibility: Literal["always", "never"] = "always",
        density: str = "default",
        accent: str | None = None,
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
            "enable_removing": enable_removing,
            "enable_dragging": enable_dragging,
            "striped": striped,
            "show_separator": show_separator,
            "scrollbar_visibility": scrollbar_visibility,
            "density": density,
        }
        if items is not None:
            internal_kwargs["items"] = items
        if datasource is not None:
            internal_kwargs["datasource"] = datasource
        if accent is not None:
            internal_kwargs["accent"] = accent
        internal_kwargs.update(kwargs)

        self._internal = _InternalListView(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

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

    def on_item_click(self, callback: Callable) -> str:
        """Register a callback for `<<ItemClick>>` events.

        Args:
            callback: Receives `event.data` — the record dict with `selected`,
                `focused`, and `item_index` injected.

        Returns:
            Bind ID — pass to `off_item_click()` to unsubscribe.
        """
        return self._internal.on_item_click(callback)

    def off_item_click(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<ItemClick>>`.

        Args:
            bind_id: ID returned by `on_item_click()`. If `None`, removes all.
        """
        self._internal.off_item_click(bind_id)

    def on_selection_changed(self, callback: Callable) -> str:
        """Register a callback for `<<SelectionChange>>` events.

        Args:
            callback: Called when selection changes. Use `get_selected()` to
                read the current selection.

        Returns:
            Bind ID — pass to `off_selection_changed()` to unsubscribe.
        """
        return self._internal.on_selection_changed(callback)

    def off_selection_changed(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<SelectionChange>>`.

        Args:
            bind_id: ID returned by `on_selection_changed()`. If `None`, removes all.
        """
        self._internal.off_selection_changed(bind_id)

    def on_item_delete(self, callback: Callable) -> str:
        """Register a callback for `<<ItemDelete>>` events.

        Args:
            callback: Receives `event.data` — the deleted record dict.

        Returns:
            Bind ID — pass to `off_item_delete()` to unsubscribe.
        """
        return self._internal.on_item_delete(callback)

    def off_item_delete(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<ItemDelete>>`.

        Args:
            bind_id: ID returned by `on_item_delete()`. If `None`, removes all.
        """
        self._internal.off_item_delete(bind_id)

    def on_item_insert(self, callback: Callable) -> str:
        """Register a callback for `<<ItemInsert>>` events.

        Args:
            callback: Receives `event.data` — the inserted record dict.

        Returns:
            Bind ID — pass to `off_item_insert()` to unsubscribe.
        """
        return self._internal.on_item_insert(callback)

    def off_item_insert(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<ItemInsert>>`.

        Args:
            bind_id: ID returned by `on_item_insert()`. If `None`, removes all.
        """
        self._internal.off_item_insert(bind_id)

    def on_item_drag_end(self, callback: Callable) -> str:
        """Register a callback for `<<ItemDragEnd>>` events.

        Args:
            callback: Receives `event.data` — record dict plus `source_index`,
                `target_index`, `moved`, `y_start`, and `y_end`.

        Returns:
            Bind ID — pass to `off_item_drag_end()` to unsubscribe.
        """
        return self._internal.on_item_drag_end(callback)

    def off_item_drag_end(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<ItemDragEnd>>`.

        Args:
            bind_id: ID returned by `on_item_drag_end()`. If `None`, removes all.
        """
        self._internal.off_item_drag_end(bind_id)

    # ----- Properties -----

    @property
    def datasource(self) -> Any:
        """The underlying `DataSourceProtocol` instance."""
        return self._internal.get_datasource()