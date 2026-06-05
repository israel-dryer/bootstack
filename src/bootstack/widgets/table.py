from __future__ import annotations

from typing import Any, Callable, Literal

from bootstack.widgets._impl.composites.tableview.tableview import (
    TableView as _InternalTableView,
)
from bootstack.events import RowEvent, RowsEvent, SelectionEvent
from bootstack.widgets._core.base import PublicWidgetBase


class Table(PublicWidgetBase):
    """A feature-rich data table with sorting, filtering, search, and grouping.

    Backed by an in-memory `SqliteDataSource`. Supply `rows=` to pre-load
    data, or pass an existing `data_source=` for a shared data source.

    Note: `data_source` must be a `SqliteDataSource`. `MemoryDataSource` and
    `FileDataSource` are not accepted.

    Args:
        columns: Column definitions — list of column-ID strings or dicts with
            keys `'text'`, `'key'`, `'width'`, and `'minwidth'`.
        rows: Initial data rows (list of dicts or sequences).
        data_source: Existing `SqliteDataSource` to use instead of creating one.
        selection_mode: `'none'`, `'single'` (default), or `'multi'`.
        sorting_mode: `'single'` (default) or `'none'`.
        searchable: Show the search bar. Default `True`.
        allow_filter: Enable column filtering. Default `True`.
        paging_mode: `'standard'` (default, paginated) or `'virtual'`.
        page_size: Rows per page in standard paging mode. Default `25`.
        allow_add: Allow adding rows via a form dialog. Default `False`.
        allow_edit: Allow editing rows via a form dialog. Default `False`.
        allow_delete: Allow deleting rows. Default `False`.
        allow_export: Enable CSV/Excel export. Default `False`.
        striped: Alternate row background colors. Default `False`.
        allow_group: Allow grouping rows by a column. Default `False`.
        show_status_bar: Show filter/sort/group status and pager. Default `True`.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        *,
        columns: list[str | dict] | None = None,
        rows: list | None = None,
        data_source: Any = None,
        selection_mode: Literal["none", "single", "multi"] = "single",
        sorting_mode: Literal["single", "none"] = "single",
        searchable: bool = True,
        allow_filter: bool = True,
        paging_mode: Literal["standard", "virtual"] = "standard",
        page_size: int = 25,
        allow_add: bool = False,
        allow_edit: bool = False,
        allow_delete: bool = False,
        allow_export: bool = False,
        striped: bool = False,
        allow_group: bool = False,
        show_status_bar: bool = True,
        show_column_chooser: bool = False,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "selection_mode": selection_mode,
            "sorting_mode": sorting_mode,
            "enable_search": searchable,
            "enable_filtering": allow_filter,
            "paging_mode": paging_mode,
            "page_size": page_size,
            "enable_adding": allow_add,
            "enable_editing": allow_edit,
            "enable_deleting": allow_delete,
            "enable_exporting": allow_export,
            "striped": striped,
            "allow_grouping": allow_group,
            "show_table_status": show_status_bar,
            "show_column_chooser": show_column_chooser,
        }
        if columns is not None:
            internal_kwargs["columns"] = columns
        if rows is not None:
            internal_kwargs["rows"] = rows
        if data_source is not None:
            internal_kwargs["datasource"] = data_source
        internal_kwargs.update(kwargs)

        self._internal = _InternalTableView(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Data -----

    def insert_rows(self, rows: list) -> None:
        """Insert new rows.

        Args:
            rows: List of dicts or sequences to insert.
        """
        self._internal.insert_rows(rows)

    def update_rows(self, rows: list[dict]) -> None:
        """Update existing rows by merging the given dicts.

        Args:
            rows: List of dicts, each with an `'id'` key and updated fields.
        """
        self._internal.update_rows(rows)

    def delete_rows(self, rows_or_ids: list) -> None:
        """Delete rows by IID or by record dict.

        Args:
            rows_or_ids: List of IID strings or record dicts with an `'id'` key.
        """
        self._internal.delete_rows(rows_or_ids)

    # ----- Selection -----

    def select_rows(self, iids: list[str]) -> None:
        """Programmatically select rows by IID.

        Args:
            iids: List of Treeview internal IDs to select.
        """
        self._internal.select_rows(iids)

    def select_all(self) -> None:
        """Select all rows in the current view."""
        self._internal.select_all()

    @property
    def selected_rows(self) -> list[dict]:
        """Currently selected record dicts."""
        return self._internal.selected_rows

    # ----- Scroll -----

    def scroll_to_row(self, iid: str) -> None:
        """Scroll the table so the given row is visible.

        Args:
            iid: Treeview internal ID of the row.
        """
        self._internal.scroll_to_row(iid)

    # ----- Filter / sort / group -----

    def get_filters(self) -> str:
        """Return the current filter expression string."""
        return self._internal.get_filters()

    def clear_filters(self) -> None:
        """Remove all active column filters."""
        self._internal.clear_filters()

    def get_sorting(self) -> dict[str, bool]:
        """Return the current sort state as `{column_key: ascending}` dict."""
        return self._internal.get_sorting()

    def clear_sorting(self) -> None:
        """Remove all active sort orders."""
        self._internal.clear_sorting()

    def get_grouping(self) -> str | None:
        """Return the currently grouped column key, or `None`."""
        return self._internal.get_grouping()

    def clear_grouping(self) -> None:
        """Remove the active grouping."""
        self._internal.clear_grouping()

    # ----- Events -----

    def on_selection_changed(
        self, callback: Callable[["SelectionEvent"], None]
    ) -> str:
        """Register a callback for `<<SelectionChange>>` events.

        Args:
            callback: Receives `event.data` — a `SelectionEvent` payload
                with `records` and `iids`.

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

    def on_row_click(
        self, callback: Callable[["RowEvent"], None]
    ) -> str:
        """Register a callback for `<<RowClick>>` events.

        Args:
            callback: Receives `event.data` — a `RowEvent` payload
                with `record` and `iid`.

        Returns:
            Bind ID — pass to `off_row_click()` to unsubscribe.
        """
        return self._internal.on_row_click(callback)

    def off_row_click(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<RowClick>>`.

        Args:
            bind_id: ID returned by `on_row_click()`. If `None`, removes all.
        """
        self._internal.off_row_click(bind_id)

    def on_row_double_click(
        self, callback: Callable[["RowEvent"], None]
    ) -> str:
        """Register a callback for `<<RowDoubleClick>>` events.

        Args:
            callback: Receives `event.data` — a `RowEvent` payload
                with `record` and `iid`.

        Returns:
            Bind ID — pass to `off_row_double_click()` to unsubscribe.
        """
        return self._internal.on_row_double_click(callback)

    def off_row_double_click(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<RowDoubleClick>>`.

        Args:
            bind_id: ID returned by `on_row_double_click()`. If `None`, removes all.
        """
        self._internal.off_row_double_click(bind_id)

    def on_row_right_click(
        self, callback: Callable[["RowEvent"], None]
    ) -> str:
        """Register a callback for `<<RowRightClick>>` events.

        Args:
            callback: Receives `event.data` — a `RowEvent` payload
                with `record` and `iid`.

        Returns:
            Bind ID — pass to `off_row_right_click()` to unsubscribe.
        """
        return self._internal.on_row_right_click(callback)

    def off_row_right_click(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<RowRightClick>>`.

        Args:
            bind_id: ID returned by `on_row_right_click()`. If `None`, removes all.
        """
        self._internal.off_row_right_click(bind_id)

    def on_row_deleted(
        self, callback: Callable[["RowsEvent"], None]
    ) -> str:
        """Register a callback for `<<RowDelete>>` events.

        Args:
            callback: Receives `event.data` — a `RowsEvent` payload
                with `records`.

        Returns:
            Bind ID — pass to `off_row_deleted()` to unsubscribe.
        """
        return self._internal.on_row_deleted(callback)

    def off_row_deleted(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<RowDelete>>`.

        Args:
            bind_id: ID returned by `on_row_deleted()`. If `None`, removes all.
        """
        self._internal.off_row_deleted(bind_id)

    def on_row_inserted(
        self, callback: Callable[["RowsEvent"], None]
    ) -> str:
        """Register a callback for `<<RowInsert>>` events.

        Args:
            callback: Receives `event.data` — a `RowsEvent` payload
                with `records`.

        Returns:
            Bind ID — pass to `off_row_inserted()` to unsubscribe.
        """
        return self._internal.on_row_inserted(callback)

    def off_row_inserted(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<RowInsert>>`.

        Args:
            bind_id: ID returned by `on_row_inserted()`. If `None`, removes all.
        """
        self._internal.off_row_inserted(bind_id)
