from __future__ import annotations

from typing import Any, Callable, Literal, Protocol, overload

from bootstack.widgets._impl.composites.tableview.tableview import (
    TableView as _InternalTableView,
)
from bootstack.data.types import DataSourceProtocol
from bootstack.events import RowEvent, RowsEvent, SelectionEvent, ExportEvent, Subscription
from bootstack.streams import Stream
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets.types import (
    ColumnSpec, FormOptions, WidgetDensity, ExportScope, ExportFormat, SelectionMode,
)


class ExportJob(Protocol):
    """Handle for an in-progress async export (returned by `export_file_async`)."""

    def cancel(self) -> None:
        """Stop the export. The partial file is removed."""
        ...


class DataTable(PublicWidgetBase):
    """A feature-rich data table with sorting, filtering, search, and grouping.

    Backed by an in-memory `SqliteDataSource` by default. Supply `rows=` to
    pre-load data, or pass an existing `data_source=` to share any data source
    that implements the data-source protocol (`SqliteDataSource`,
    `MemoryDataSource`, `FileDataSource`, or your own).

    Args:
        columns: Column definitions — a list of field-key strings, or
            `ColumnSpec` dicts (`'key'`, `'text'`, `'width'`, `'minwidth'`,
            `'anchor'`, and the editor keys `'editor'`, `'editor_options'`,
            `'dtype'`, `'readonly'`, `'required'` that shape the add/edit dialog).
        rows: Initial data rows (list of dicts or sequences).
        data_source: Existing data source to use instead of creating one. Any
            object implementing the data-source protocol is accepted
            (`SqliteDataSource`, `MemoryDataSource`, `FileDataSource`, or a
            custom source).
        selection_mode: Row selection behavior. Default `'single'`.
        sorting_mode: Whether columns can be sorted. Default `'single'`.
        searchable: Show the search bar. Default `True`.
        allow_filter: Enable column filtering. Default `True`.
        paging_mode: `'standard'` paginates the rows; `'virtual'` scrolls them
            in a single virtual view. Default `'standard'`.
        page_size: Rows per page in standard paging mode. Default `25`.
        allow_add: Allow adding rows via a form dialog. Default `False`.
        allow_edit: Allow editing rows via a form dialog. Default `False`.
        allow_delete: Allow deleting rows. Default `False`.
        allow_export: Show an export menu (Copy to clipboard / Save to file).
            The actions export the selected rows if any are selected, otherwise
            all rows in the current filter/sort. Saves CSV; Excel (`.xlsx`) is
            also offered when the optional `bootstack[excel]` dependency is
            installed. For explicit control use `export_file()` / `to_csv()`
            with `scope=`. Default `False`.
        export_formats: Which formats the export menu offers. Default `('csv',)`.
            Formats needing an optional dependency (`xlsx`→`bootstack[excel]`,
            `parquet`/`feather`→`bootstack[parquet]`, `hdf5`→`bootstack[hdf5]`)
            appear only when it is installed. Registry formats export the
            displayed columns; for the full record set use `data_source.save(path)`.
        striped: Alternate row background colors. Default `True`.
        density: Row compactness — `'default'` or `'compact'` (tighter row
            height, smaller body font and padding). Default `'default'`.
        allow_group: Allow grouping rows by a column. Default `False`.
        show_status_bar: Show the footer — the filter/sort/group status and the
            pager. The pager auto-hides on a single page, and the whole footer
            collapses when there's nothing to show. Default `True`.
        show_column_chooser: Show a button to toggle column visibility.
            Default `False`.
        show_selection_controls: Show a per-row checkbox in the leading icon slot
            while in `'multi'` selection mode — filled with the accent when
            selected, a muted outline otherwise. With the checkboxes visible, a
            plain click toggles the row (no Ctrl/Shift needed). Has no effect in
            `'single'` mode (the row highlight is enough) or while grouped, where
            the slot holds the group's expand/collapse control. Default `False`.
        id_field: Record field used as the stable row identity. When your rows
            carry this field (default `'id'`), its value becomes the row id used
            by `select_rows`, events, and `update_rows`/`delete_rows`, so your own
            ids round-trip; otherwise an id is auto-assigned. Ignored when you pass
            your own `data_source` (set it on the source instead). Default `'id'`.
        form: Layout options for the built-in add/edit dialog — a `FormOptions`
            dict (`col_count`, `min_col_width`, `scrollable`, `resizable`).
        parent: Override the context-stack parent.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        *,
        columns: list[str | ColumnSpec] | None = None,
        rows: list | None = None,
        data_source: DataSourceProtocol | None = None,
        selection_mode: SelectionMode = "single",
        sorting_mode: Literal["single", "none"] = "single",
        searchable: bool = True,
        allow_filter: bool = True,
        paging_mode: Literal["standard", "virtual"] = "standard",
        page_size: int = 25,
        allow_add: bool = False,
        allow_edit: bool = False,
        allow_delete: bool = False,
        allow_export: bool = False,
        export_formats: list[
            Literal["csv", "tsv", "xlsx", "json", "jsonl", "xml", "parquet", "feather", "hdf5"]
        ] | None = None,
        striped: bool = True,
        density: WidgetDensity = "default",
        allow_group: bool = False,
        show_status_bar: bool = True,
        show_column_chooser: bool = False,
        show_selection_controls: bool = False,
        id_field: str = "id",
        form: FormOptions | None = None,
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
            "density": density,
            "allow_grouping": allow_group,
            "show_table_status": show_status_bar,
            "show_column_chooser": show_column_chooser,
            "show_selection_controls": show_selection_controls,
            "id_field": id_field,
        }
        if columns is not None:
            internal_kwargs["columns"] = columns
        if rows is not None:
            internal_kwargs["rows"] = rows
        if data_source is not None:
            internal_kwargs["datasource"] = data_source
        if form is not None:
            internal_kwargs["form_options"] = form
        if export_formats is not None:
            internal_kwargs["export_formats"] = tuple(export_formats)

        self._internal = _InternalTableView(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Data -----

    def set_rows(self, rows: list) -> None:
        """Replace the entire dataset with `rows`.

        Args:
            rows: List of dicts (or sequences) to load.
        """
        self._internal.set_data(rows)

    def insert_rows(self, rows: list) -> None:
        """Insert new rows.

        Args:
            rows: List of dicts or sequences to insert.
        """
        self._internal.insert_rows(rows)

    def update_rows(self, rows: list[dict]) -> None:
        """Update existing rows by merging the given dicts.

        Args:
            rows: List of dicts, each with an `id` key and the fields to update.
        """
        self._internal.update_rows(rows)

    def delete_rows(self, rows_or_ids: list) -> None:
        """Delete rows by record `id` or by record dict.

        Args:
            rows_or_ids: List of record ids or record dicts with an `id` key.
        """
        self._internal.delete_rows(rows_or_ids)

    def new_row(self, defaults: dict | None = None) -> dict | None:
        """Open the built-in *New Record* dialog and insert on save.

        Honors each column's editor configuration (`editor`, `dtype`,
        `readonly`, `required`). On save the row is inserted and an `rows_insert`
        event fires; the saved record is also returned here.

        Args:
            defaults: Field values to pre-fill the form with.

        Returns:
            The new record, or `None` if the dialog was cancelled.
        """
        return self._internal.new_row(defaults)

    def edit_row(self, record_id: Any) -> dict | None:
        """Open the built-in *Edit Record* dialog for a row and save on submit.

        On save the row is updated and a `rows_update` event fires (or
        `rows_delete` if the user deletes it); the saved record is also returned.

        Args:
            record_id: Record id of the row to edit.

        Returns:
            The updated record, or `None` if cancelled or deleted.
        """
        return self._internal.edit_row(record_id)

    # ----- Selection -----

    def select_rows(self, record_ids: list) -> None:
        """Select rows by record `id`.

        Only rows on the current page can be selected.

        Args:
            record_ids: Record ids of the rows to select.
        """
        self._internal.select_rows(record_ids)

    def select_all(self) -> None:
        """Select all rows in the current view."""
        self._internal.select_all()

    def deselect_rows(self, record_ids: list) -> None:
        """Remove the given rows from the selection by record `id`.

        Args:
            record_ids: Record ids to deselect.
        """
        self._internal.deselect_rows(record_ids)

    def clear_selection(self) -> None:
        """Clear the selection.

        Users can also press `Escape` over the table to clear it — useful in
        single-select mode, where clicking cannot return to an empty selection.
        """
        self._internal.deselect_all()

    @property
    def selected_rows(self) -> list[dict]:
        """Currently selected record dicts."""
        return self._internal.selected_rows

    # ----- Scroll -----

    def scroll_to_row(self, record_id: Any) -> None:
        """Scroll the table so the row with the given `id` is visible.

        Args:
            record_id: Record id of the row.
        """
        self._internal.scroll_to_row(record_id)

    # ----- Paging -----

    def go_to_page(self, index: int) -> None:
        """Show the page at the given zero-based index.

        Args:
            index: Zero-based page index.
        """
        self._internal.go_to_page(index)

    def next_page(self) -> None:
        """Advance to the next page (no-op on the last page)."""
        self._internal.next_page()

    def prev_page(self) -> None:
        """Go to the previous page (no-op on the first page)."""
        self._internal.previous_page()

    @property
    def current_page(self) -> int:
        """Zero-based index of the page currently shown."""
        return self._internal.current_page

    @property
    def page_count(self) -> int:
        """Total number of pages for the current filter/search."""
        return self._internal.page_count

    # ----- Export -----

    def to_rows(self, scope: ExportScope = "all", *, max_rows: int | None = 100_000) -> list[dict]:
        """Return the data as a list of record dicts (materialized — small data).

        Loads every matching row into memory. For large datasets use
        `iter_rows()` (streaming) or `export_file()` instead.

        Args:
            scope: Which rows — `'all'` (the filtered set), `'page'` (current
                page), or `'selection'` (selected rows).
            max_rows: Raise if the row count exceeds this. Pass `None` to lift
                the cap (at your own memory risk).
        """
        return self._internal.to_rows(scope, max_rows=max_rows)

    def to_csv(self, scope: ExportScope = "all", *, max_rows: int | None = 100_000) -> str:
        """Return the data as a CSV string (materialized — small data).

        For large datasets use `export_file()`, which streams to disk.

        Args:
            scope: `'all'`, `'page'`, or `'selection'`.
            max_rows: Raise if the row count exceeds this. `None` lifts the cap.
        """
        return self._internal.to_csv(scope, max_rows=max_rows)

    def iter_rows(self, scope: ExportScope = "all", chunk_size: int = 1000):
        """Lazily yield record dicts one at a time, paging the data source.

        Memory stays flat regardless of size — suitable for very large exports.

        Args:
            scope: `'all'`, `'page'`, or `'selection'`.
            chunk_size: Rows read from the source per batch.
        """
        return self._internal.iter_rows(scope, chunk_size)

    def export_file(
        self,
        path: str,
        scope: ExportScope = "all",
        *,
        format: ExportFormat | None = None,
        chunk_size: int = 1000,
        on_progress: Callable[[int, int], Any] | None = None,
    ) -> int:
        """Stream the data to `path`, paging so memory stays flat.

        The format is inferred from the path extension (`.csv`, `.tsv`, `.xlsx`)
        unless `format` is given. `.xlsx` requires `bootstack[excel]`.

        Args:
            path: Destination file path.
            scope: `'all'`, `'page'`, or `'selection'`.
            format: Override the format — `'csv'`, `'tsv'`, or `'xlsx'`.
            chunk_size: Rows read/written per batch.
            on_progress: Called as `on_progress(written, total)` after each batch.

        Returns:
            The number of rows written.
        """
        return self._internal.export_file(
            path, scope, format=format, chunk_size=chunk_size, on_progress=on_progress
        )

    def export_file_async(
        self,
        path: str,
        scope: ExportScope = "all",
        *,
        format: ExportFormat | None = None,
        chunk_size: int = 1000,
        on_progress: Callable[[int, int], Any] | None = None,
        on_done: Callable[[str, int, Any], Any] | None = None,
    ) -> ExportJob:
        """Stream the data to `path` without blocking the UI; return a job.

        Writes one chunk per event-loop idle tick, so the UI stays responsive
        and the export can be cancelled mid-run via the returned job's
        `cancel()`. A cancelled or failed export removes the partial file.

        Args:
            path: Destination file path.
            scope: `'all'`, `'page'`, or `'selection'`.
            format: Override the format — `'csv'`, `'tsv'`, or `'xlsx'`.
            chunk_size: Rows read/written per idle tick.
            on_progress: Called as `on_progress(written, total)` after each chunk.
            on_done: Called as `on_done(status, written, error)` at the end, with
                `status` one of `'completed'`, `'cancelled'`, or `'error'`.

        Returns:
            A job handle with a `cancel()` method.
        """
        return self._internal.export_file_async(
            path, scope, format=format, chunk_size=chunk_size,
            on_progress=on_progress, on_done=on_done,
        )

    # ----- Search -----

    def get_search(self) -> str:
        """Return the active free-text search term."""
        return self._internal.get_search()

    def set_search(self, text: str) -> None:
        """Set the free-text search term.

        Searches across all columns. Leaves any active column filters intact.

        Args:
            text: The search term. Pass an empty string to clear the search.
        """
        self._internal.set_search(text)

    def clear_search(self) -> None:
        """Clear the free-text search term (leaves column filters intact)."""
        self._internal.clear_search()

    # ----- Filter / sort / group -----

    def get_filters(self) -> dict[str, list]:
        """Return the active column filters as `{column_key: allowed_values}`."""
        return self._internal.get_filters()

    def clear_filters(self) -> None:
        """Remove all active column filters (leaves the search term intact)."""
        self._internal.clear_filters()

    def set_filter(self, column: str, values: list | None = None) -> None:
        """Filter a column to the given values, or clear it when `values` is None.

        Composes with the search term and other column filters.

        Args:
            column: Column key to filter.
            values: Allowed values; `None` clears this column's filter.
        """
        self._internal.set_filter(column, values)

    def get_sorting(self) -> dict[str, bool]:
        """Return the current sort state as `{column_key: ascending}` dict."""
        return self._internal.get_sorting()

    def clear_sorting(self) -> None:
        """Remove all active sort orders."""
        self._internal.clear_sorting()

    def sort_by(self, column: str, ascending: bool = True) -> None:
        """Sort the table by a column.

        Args:
            column: Column key to sort by.
            ascending: Sort ascending (default) or descending.
        """
        self._internal.set_sorting(column, ascending)

    def get_grouping(self) -> str | None:
        """Return the currently grouped column key, or `None`."""
        return self._internal.get_grouping()

    def clear_grouping(self) -> None:
        """Remove the active grouping."""
        self._internal.clear_grouping()

    def group_by(self, column: str) -> None:
        """Group rows by a column (collapsible group headers).

        Args:
            column: Column key to group by.
        """
        self._internal.set_grouping(column)

    def expand_all(self) -> None:
        """Expand all groups."""
        self._internal.expand_all()

    def collapse_all(self) -> None:
        """Collapse all groups."""
        self._internal.collapse_all()

    # ----- Properties -----

    @property
    def data_source(self) -> DataSourceProtocol:
        """The underlying data source instance."""
        return self._internal._datasource

    # ----- Events -----

    @overload
    def on_selection_changed(self) -> Stream: ...
    @overload
    def on_selection_changed(self, handler: Callable[[SelectionEvent], Any]) -> Subscription: ...
    def on_selection_changed(self, handler: Callable[[SelectionEvent], Any] | None = None) -> Stream | Subscription:
        """Fired when the set of selected rows changes.

        Args:
            handler: Called with a :class:`~bootstack.events.SelectionEvent`
                (`records`, `ids`). Omit to get a composable
                :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("selection_changed", handler)

    @overload
    def on_row_click(self) -> Stream: ...
    @overload
    def on_row_click(self, handler: Callable[[RowEvent], Any]) -> Subscription: ...
    def on_row_click(self, handler: Callable[[RowEvent], Any] | None = None) -> Stream | Subscription:
        """Fired when a row is clicked.

        Args:
            handler: Called with a :class:`~bootstack.events.RowEvent` (`record`,
                `id`). Omit to get a composable
                :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("row_click", handler)

    @overload
    def on_row_double_click(self) -> Stream: ...
    @overload
    def on_row_double_click(self, handler: Callable[[RowEvent], Any]) -> Subscription: ...
    def on_row_double_click(self, handler: Callable[[RowEvent], Any] | None = None) -> Stream | Subscription:
        """Fired when a row is double-clicked.

        Args:
            handler: Called with a :class:`~bootstack.events.RowEvent` (`record`,
                `id`). Omit to get a composable
                :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("row_double_click", handler)

    @overload
    def on_row_right_click(self) -> Stream: ...
    @overload
    def on_row_right_click(self, handler: Callable[[RowEvent], Any]) -> Subscription: ...
    def on_row_right_click(self, handler: Callable[[RowEvent], Any] | None = None) -> Stream | Subscription:
        """Fired when a row is right-clicked.

        Args:
            handler: Called with a :class:`~bootstack.events.RowEvent` (`record`,
                `id`). Omit to get a composable
                :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("row_right_click", handler)

    @overload
    def on_rows_insert(self) -> Stream: ...
    @overload
    def on_rows_insert(self, handler: Callable[[RowsEvent], Any]) -> Subscription: ...
    def on_rows_insert(self, handler: Callable[[RowsEvent], Any] | None = None) -> Stream | Subscription:
        """Fired after rows are inserted.

        Args:
            handler: Called with a :class:`~bootstack.events.RowsEvent` carrying
                the inserted `records`. Omit to get a composable
                :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("rows_insert", handler)

    @overload
    def on_rows_update(self) -> Stream: ...
    @overload
    def on_rows_update(self, handler: Callable[[RowsEvent], Any]) -> Subscription: ...
    def on_rows_update(self, handler: Callable[[RowsEvent], Any] | None = None) -> Stream | Subscription:
        """Fired after rows are updated.

        Args:
            handler: Called with a :class:`~bootstack.events.RowsEvent` carrying
                the updated `records`. Omit to get a composable
                :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("rows_update", handler)

    @overload
    def on_rows_delete(self) -> Stream: ...
    @overload
    def on_rows_delete(self, handler: Callable[[RowsEvent], Any]) -> Subscription: ...
    def on_rows_delete(self, handler: Callable[[RowsEvent], Any] | None = None) -> Stream | Subscription:
        """Fired after rows are deleted.

        Args:
            handler: Called with a :class:`~bootstack.events.RowsEvent` carrying
                the deleted `records`. Omit to get a composable
                :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("rows_delete", handler)

    @overload
    def on_rows_move(self) -> Stream: ...
    @overload
    def on_rows_move(self, handler: Callable[[RowsEvent], Any]) -> Subscription: ...
    def on_rows_move(self, handler: Callable[[RowsEvent], Any] | None = None) -> Stream | Subscription:
        """Fired after rows are reordered.

        Args:
            handler: Called with a :class:`~bootstack.events.RowsEvent` carrying
                the moved `records`. Omit to get a composable
                :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("rows_move", handler)

    @overload
    def on_export(self) -> Stream: ...
    @overload
    def on_export(self, handler: Callable[[ExportEvent], Any]) -> Subscription: ...
    def on_export(self, handler: Callable[[ExportEvent], Any] | None = None) -> Stream | Subscription:
        """Fired after the data is exported (copied or saved).

        Args:
            handler: Called with an :class:`~bootstack.events.ExportEvent`
                (`count`, `target` — `'clipboard'` or `'file'` — `format`, and
                `path`). Omit to get a composable
                :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("export", handler)


_DATATABLE_EVENTS: dict[str, str] = {
    "selection_changed": "<<SelectionChange>>",
    "row_click":         "<<RowClick>>",
    "row_double_click":  "<<RowDoubleClick>>",
    "row_right_click":   "<<RowRightClick>>",
    "rows_insert":        "<<RowsInsert>>",
    "rows_update":        "<<RowsUpdate>>",
    "rows_delete":        "<<RowsDelete>>",
    "rows_move":          "<<RowsMove>>",
    "export":            "<<Export>>",
}

register_widget_events(DataTable, _DATATABLE_EVENTS)
